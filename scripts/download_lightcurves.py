"""Batch light curve retrieval and persistent caching script using Lightkurve and NASA MAST."""
import argparse
import logging
import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Download and cache Kepler light curves from NASA MAST.")
    parser.add_argument("--kepid", type=int, default=None, help="Specific Kepler ID (e.g. 11442793 for Kepler-90)")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of stars to download (default: 100)")
    parser.add_argument("--force-refresh", action="store_true", help="Force re-download even if already cached")
    parser.add_argument("--include-kepler90", action="store_true", default=True, help="Always ensure Kepler-90 is downloaded")
    args = parser.parse_args()

    cache = LightCurveCache()
    cached_stars = set(cache.list_cached_stars())
    logger.info(f"Currently cached stars on disk: {len(cached_stars)}")

    if args.kepid is not None:
        targets = [args.kepid]
    else:
        # Load cleaned TCEs to select balanced sample of stars
        tce_path = cfg.processed_dir / "tce_cleaned.csv"
        if not tce_path.exists():
            logger.error("Cleaned TCE dataset not found. Run scripts/prepare_dataset.py first.")
            sys.exit(1)

        df = pd.read_csv(tce_path)
        # Separate stars by PC vs False Positive
        star_max_label = df.groupby("kepid")["planet"].max()
        pc_stars = star_max_label[star_max_label == 1].index.tolist()
        non_pc_stars = star_max_label[star_max_label == 0].index.tolist()

        # Prioritize Kepler-90 first
        targets = []
        if args.include_kepler90 and cfg.kepler90_kepid not in targets:
            targets.append(cfg.kepler90_kepid)

        # Alternating sample of PC and Non-PC stars
        half_limit = args.limit // 2
        for s in pc_stars:
            if len(targets) >= half_limit:
                break
            if s not in targets:
                targets.append(s)

        for s in non_pc_stars:
            if len(targets) >= args.limit:
                break
            if s not in targets:
                targets.append(s)

    logger.info(f"Target download list: {len(targets)} stars.")

    downloaded = 0
    already_cached = 0
    failed = 0

    pbar = tqdm(targets, desc="Fetching Kepler Light Curves")
    for kid in pbar:
        if cache.exists(kid) and not args.force_refresh:
            already_cached += 1
            pbar.set_postfix({"cached": already_cached, "new": downloaded, "failed": failed})
            continue

        t, f, fe, meta = download_stellar_lightcurve(kid, cache=cache, force_refresh=args.force_refresh)
        if t is not None:
            downloaded += 1
        else:
            failed += 1
        pbar.set_postfix({"cached": already_cached, "new": downloaded, "failed": failed})

    logger.info("=" * 60)
    logger.info("LIGHT CURVE DOWNLOAD SUMMARY:")
    logger.info(f"  Total targets processed: {len(targets)}")
    logger.info(f"  Newly downloaded & cached: {downloaded}")
    logger.info(f"  Already in persistent cache: {already_cached}")
    logger.info(f"  Failed / Unavailable: {failed}")
    logger.info(f"  Total stars now in cache: {len(cache.list_cached_stars())}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

