"""
pipeline.py
-----------
Single entry point that runs the full data pipeline end-to-end:

    ingestion → cleaning → transformation → feature engineering → marts

Usage:
    python pipeline.py                           # default ~10k rows
    USE_SCALED_DATA=1 python pipeline.py         # synthetic 500k rows
"""

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from cleaning import clean, save_clean
from feature_engineering import engineer_features
from ingestion import ingest
from marts import build_all_marts
from transformation import transform

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
SCALED_CSV = PROJECT_ROOT / "data" / "raw" / "Superstore_500k.csv"


def run() -> None:
    logger.info("=== Superstore Pipeline START ===")

    use_scaled = os.getenv("USE_SCALED_DATA", "0") == "1"

    if use_scaled:
        if not SCALED_CSV.exists():
            raise FileNotFoundError(
                f"Scaled dataset not found at {SCALED_CSV}. "
                "Run `python scripts/generate_scale_data.py` first."
            )
        logger.info(f"Using scaled dataset: {SCALED_CSV}")
        df = ingest(SCALED_CSV)
    else:
        df = ingest()

    df = clean(df)
    save_clean(df)
    df = transform(df)
    df = engineer_features(df)
    build_all_marts(df)

    logger.info("=== Superstore Pipeline COMPLETE ===")


if __name__ == "__main__":
    run()
