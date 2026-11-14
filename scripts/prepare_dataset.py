"""Dataset preparation script: fetch labels, clean dataset, and perform grouped star splits."""
import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.data_loader import get_or_build_tce_catalog, clean_and_filter_tce_data, create_grouped_splits


def main():
    print("=" * 70)
    print("PHASE 2: PREPARING NASA KEPLER DR24 TCE DATASET")
    print("=" * 70)

    # 1. Ingest / Build Catalog
    df_catalog = get_or_build_tce_catalog()
    print(f"Total catalog rows loaded: {len(df_catalog)}")

    # 2. Clean and Filter
    df_clean, audit = clean_and_filter_tce_data(df_catalog)
    cleaned_path = cfg.processed_dir / "tce_cleaned.csv"
    df_clean.to_csv(cleaned_path, index=False)
    print(f"Cleaned dataset saved to: {cleaned_path}")

    with open(cfg.metrics_dir / "cleaning_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    # 3. Grouped Star Splitting (80/10/10)
    df_train, df_val, df_test, split_info = create_grouped_splits(
        df_clean,
        train_ratio=cfg.train_split,
        val_ratio=cfg.val_split,
        test_ratio=cfg.test_split,
        random_seed=cfg.random_seed,
    )

    df_train.to_csv(cfg.processed_dir / "tce_train.csv", index=False)
    df_val.to_csv(cfg.processed_dir / "tce_val.csv", index=False)
    df_test.to_csv(cfg.processed_dir / "tce_test.csv", index=False)

    print("\nDataset Preparation Completed Successfully:")
    print(f"  - Total Cleaned TCEs: {len(df_clean)}")
    print(f"  - Unique Stars:       {audit['unique_stars']}")
    print(f"  - Training Stars:     {split_info['train']['num_stars']} ({len(df_train)} TCEs, {split_info['train']['planet_candidates']} PCs)")
    print(f"  - Validation Stars:   {split_info['val']['num_stars']} ({len(df_val)} TCEs, {split_info['val']['planet_candidates']} PCs)")
    print(f"  - Test Stars:         {split_info['test']['num_stars']} ({len(df_test)} TCEs, {split_info['test']['planet_candidates']} PCs)")
    print("=" * 70)


if __name__ == "__main__":
    main()

