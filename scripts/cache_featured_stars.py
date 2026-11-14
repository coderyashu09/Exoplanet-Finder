"""Pre-cache real NASA Kepler light curves for the 6 curated showcase catalog systems.
Ensures instant offline 3D visualization and PyTorch CNN inference.
"""
import sys
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cache_featured_stars")

FEATURED_STARS = [
    {"name": "Kepler-90", "kepid": 11442793, "notes": "8-planet system; Kepler-90i AI discovery"},
    {"name": "Kepler-186", "kepid": 8120608, "notes": "First Earth-sized habitable zone planet (186f)"},
    {"name": "Kepler-452", "kepid": 8311864, "notes": "Earth's cousin orbiting G2V solar twin (452b)"},
    {"name": "Kepler-22", "kepid": 10666592, "notes": "First confirmed habitable zone planet (22b)"},
    {"name": "Kepler-10", "kepid": 11904151, "notes": "First confirmed rocky exoplanet (10b)"},
    {"name": "Kepler-16", "kepid": 12644769, "notes": "First circumbinary planet orbiting twin stars (16b)"},
]

def main():
    cache = LightCurveCache()
    logger.info("=" * 65)
    logger.info("PRE-CACHING NASA LIGHT CURVES FOR SHOWCASE STARS")
    logger.info("=" * 65)
    
    for star in FEATURED_STARS:
        kepid = star["kepid"]
        name = star["name"]
        notes = star["notes"]
        
        if cache.exists(kepid):
            data = cache.load(kepid)
            if data is not None:
                time_arr, flux_arr, flux_err = data
                pts = len(time_arr)
                logger.info(f"✓ ALREADY CACHED: {name} (KIC {kepid}) — {pts:,} photometric cadences [{notes}]")
                continue
            
        logger.info(f"↓ Fetching {name} (KIC {kepid}) from NASA MAST via Lightkurve...")
        try:
            time, flux, flux_err, meta = download_stellar_lightcurve(kepid, cache=cache)
            if time is not None and len(time) > 0:
                logger.info(f"✓ SUCCESSFULLY CACHED: {name} (KIC {kepid}) — {len(time):,} cadences saved.")
            else:
                logger.warning(f"⚠ WARNING: No cadences returned for {name} (KIC {kepid}).")
        except Exception as e:
            logger.error(f"✗ ERROR fetching {name} (KIC {kepid}): {e}")

    cached_list = cache.list_cached_stars()
    logger.info("=" * 65)
    logger.info(f"Total cached stars in local repository: {len(cached_list)}")
    logger.info("Showcase systems ready for offline AI inference and 3D exploration.")
    logger.info("=" * 65)

if __name__ == "__main__":
    main()
