"""Data ingestion, validation, and grouped star-level splitting for NASA Kepler DR24 TCE catalog."""
import json
import logging
import urllib.parse
import urllib.request
import io
from pathlib import Path
from typing import Dict, Tuple, Any, List

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from src.config import cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def fetch_labels_from_nasa_tap() -> pd.DataFrame:
    """Fetch av_training_set labels for DR24 TCEs directly from NASA Exoplanet Archive TAP API."""
    logger.info("Connecting to NASA Exoplanet Archive TAP service to retrieve DR24 labels...")
    query = "select kepid, tce_plnt_num, av_training_set from q1_q17_dr24_tce"
    url = f"{NASA_TAP_URL}?query={urllib.parse.quote(query)}&format=csv"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ExoplanetFinder/1.0 (NASA DR24 Research Pipeline)"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
    df_labels = pd.read_csv(io.BytesIO(data))
    logger.info(f"Successfully fetched {len(df_labels)} label records from NASA TAP service.")
    return df_labels


def get_or_build_tce_catalog() -> pd.DataFrame:
    """Ensure a complete DR24 TCE catalog is available on disk with av_training_set labels.

    Preserves original files and saves the unified dataset to cfg.tce_catalog_file.
    """
    if cfg.tce_catalog_file.exists():
        logger.info(f"Loading existing complete TCE catalog from {cfg.tce_catalog_file}")
        return pd.read_csv(cfg.tce_catalog_file, comment="#")

    if not cfg.original_data_file.exists():
        raise FileNotFoundError(f"Neither {cfg.tce_catalog_file} nor {cfg.original_data_file} exists.")

    logger.info(f"Inspecting base catalog at {cfg.original_data_file}")
    df_base = pd.read_csv(cfg.original_data_file, comment="#")

    if "av_training_set" not in df_base.columns:
        logger.info("'av_training_set' missing from local file. Fetching authentic labels from NASA...")
        df_labels = fetch_labels_from_nasa_tap()
        # Merge on kepid and tce_plnt_num
        df_merged = pd.merge(
            df_base,
            df_labels,
            on=["kepid", "tce_plnt_num"],
            how="left",
            suffixes=("", "_nasa"),
        )
    else:
        df_merged = df_base

    # Save to catalog file, keeping original untouched
    cfg.tce_catalog_file.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(cfg.tce_catalog_file, index=False)
    logger.info(f"Saved complete catalog with labels ({len(df_merged)} rows) to {cfg.tce_catalog_file}")
    return df_merged


def clean_and_filter_tce_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and validate TCE dataset strictly following scientific constraints.

    1. Excludes autovetter predictions to eliminate data leakage.
    2. Excludes UNK and unlabeled rows.
    3. Maps: PC -> 1, AFP -> 0, NTP -> 0.
    4. Validates positive orbital period, duration, epoch, and valid star IDs.
    """
    total_raw = len(df)
    audit: Dict[str, Any] = {"total_raw_rows": total_raw, "exclusions": {}}

    # 1. Eliminate data leakage columns
    leakage_cols = [c for c in df.columns if c.startswith("av_pp_") or c == "av_pred_class"]
    if leakage_cols:
        df = df.drop(columns=leakage_cols)
        audit["leakage_columns_dropped"] = leakage_cols
        logger.info(f"Eliminated potential leakage columns: {leakage_cols}")

    # 2. Check label column
    if "av_training_set" not in df.columns:
        raise ValueError("Missing 'av_training_set' column in dataset.")

    # Exclude UNK and NaNs
    valid_labels_map = {"PC": 1, "AFP": 0, "NTP": 0}
    mask_known_label = df["av_training_set"].isin(valid_labels_map.keys())
    audit["exclusions"]["unknown_or_missing_label"] = int((~mask_known_label).sum())
    df_labeled = df[mask_known_label].copy()

    # 3. Scientific sanity checks
    # Positive orbital period
    mask_valid_period = df_labeled["tce_period"] > 0
    audit["exclusions"]["invalid_period"] = int((~mask_valid_period).sum())

    # Positive transit duration
    mask_valid_duration = df_labeled["tce_duration"] > 0
    audit["exclusions"]["invalid_duration"] = int((~mask_valid_duration).sum())

    # Valid transit epoch
    mask_valid_epoch = df_labeled["tce_time0bk"].notna()
    audit["exclusions"]["missing_epoch"] = int((~mask_valid_epoch).sum())

    # Valid kepid
    mask_valid_kepid = df_labeled["kepid"].notna() & (df_labeled["kepid"] > 0)
    audit["exclusions"]["invalid_kepid"] = int((~mask_valid_kepid).sum())

    combined_mask = mask_valid_period & mask_valid_duration & mask_valid_epoch & mask_valid_kepid
    df_clean = df_labeled[combined_mask].copy()

    # Assign binary target: PC=1 (planet-like), AFP/NTP=0 (non-planet)
    df_clean["planet"] = df_clean["av_training_set"].map(valid_labels_map).astype(int)

    # Document final distributions
    audit["final_valid_rows"] = len(df_clean)
    audit["unique_stars"] = int(df_clean["kepid"].nunique())
    audit["label_counts"] = {str(k): int(v) for k, v in df_clean["av_training_set"].value_counts().items()}
    audit["binary_target_counts"] = {str(k): int(v) for k, v in df_clean["planet"].value_counts().items()}

    logger.info(
        f"Cleaned TCE dataset: {len(df_clean)} / {total_raw} rows retained across {audit['unique_stars']} unique stars."
    )
    logger.info(f"Target breakdown: PC (planet=1): {audit['label_counts'].get('PC', 0)}, "
                f"AFP (false positive=0): {audit['label_counts'].get('AFP', 0)}, "
                f"NTP (non-transiting=0): {audit['label_counts'].get('NTP', 0)}")

    return df_clean, audit


def create_grouped_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Partition dataset into Train / Val / Test sets grouped strictly by star (kepid).

    Guarantees 0% star overlap between splits.
    Uses grouped splitting to prevent stellar data leakage.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Split ratios must sum to 1.0"

    stars = df["kepid"].unique()
    np.random.seed(random_seed)

    # To maintain representative label distribution, calculate star-level class indicator
    # (whether star hosts at least one planet candidate)
    star_has_pc = df.groupby("kepid")["planet"].max().to_dict()
    pc_stars = [s for s in stars if star_has_pc[s] == 1]
    non_pc_stars = [s for s in stars if star_has_pc[s] == 0]

    np.random.shuffle(pc_stars)
    np.random.shuffle(non_pc_stars)

    def split_list(items: List[int]) -> Tuple[List[int], List[int], List[int]]:
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train_items = items[:n_train]
        val_items = items[n_train : n_train + n_val]
        test_items = items[n_train + n_val :]
        return train_items, val_items, test_items

    pc_train, pc_val, pc_test = split_list(pc_stars)
    npc_train, npc_val, npc_test = split_list(non_pc_stars)

    train_stars = set(pc_train + npc_train)
    val_stars = set(pc_val + npc_val)
    test_stars = set(pc_test + npc_test)

    # VERIFY STRICT GROUP ISOLATION
    overlap_train_val = train_stars & val_stars
    overlap_train_test = train_stars & test_stars
    overlap_val_test = val_stars & test_stars

    if overlap_train_val or overlap_train_test or overlap_val_test:
        raise ValueError(
            f"Star leakage detected! "
            f"Train-Val: {len(overlap_train_val)}, "
            f"Train-Test: {len(overlap_train_test)}, "
            f"Val-Test: {len(overlap_val_test)}"
        )

    df_train = df[df["kepid"].isin(train_stars)].copy().reset_index(drop=True)
    df_val = df[df["kepid"].isin(val_stars)].copy().reset_index(drop=True)
    df_test = df[df["kepid"].isin(test_stars)].copy().reset_index(drop=True)

    # Document split metadata
    split_info = {
        "random_seed": random_seed,
        "train": {
            "num_stars": len(train_stars),
            "num_tces": len(df_train),
            "planet_candidates": int((df_train["planet"] == 1).sum()),
            "non_planets": int((df_train["planet"] == 0).sum()),
            "pc_rate": float((df_train["planet"] == 1).mean()),
        },
        "val": {
            "num_stars": len(val_stars),
            "num_tces": len(df_val),
            "planet_candidates": int((df_val["planet"] == 1).sum()),
            "non_planets": int((df_val["planet"] == 0).sum()),
            "pc_rate": float((df_val["planet"] == 1).mean()),
        },
        "test": {
            "num_stars": len(test_stars),
            "num_tces": len(df_test),
            "planet_candidates": int((df_test["planet"] == 1).sum()),
            "non_planets": int((df_test["planet"] == 0).sum()),
            "pc_rate": float((df_test["planet"] == 1).mean()),
        },
        "star_overlap_verification": {
            "train_val_overlap": 0,
            "train_test_overlap": 0,
            "val_test_overlap": 0,
            "passed": True,
        },
    }

    # Save splits to disk
    cfg.splits_dir.mkdir(parents=True, exist_ok=True)
    with open(cfg.splits_dir / "splits_summary.json", "w", encoding="utf-8") as f:
        json.dump(split_info, f, indent=2)

    with open(cfg.splits_dir / "star_splits.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "train_stars": [int(x) for x in sorted(list(train_stars))],
                "val_stars": [int(x) for x in sorted(list(val_stars))],
                "test_stars": [int(x) for x in sorted(list(test_stars))],
            },
            f,
        )

    logger.info("Grouped Star Splitting Summary:")
    logger.info(f"  Train: {len(train_stars)} stars, {len(df_train)} TCEs ({split_info['train']['planet_candidates']} PCs)")
    logger.info(f"  Val:   {len(val_stars)} stars, {len(df_val)} TCEs ({split_info['val']['planet_candidates']} PCs)")
    logger.info(f"  Test:  {len(test_stars)} stars, {len(df_test)} TCEs ({split_info['test']['planet_candidates']} PCs)")
    logger.info("Verification passed: 0% star overlap between splits.")

    return df_train, df_val, df_test, split_info
