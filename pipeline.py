"""
pipeline.py
-----------
Single entry point that runs the full data pipeline end-to-end:

    ingestion → cleaning → transformation → feature engineering → marts

Usage:
    python pipeline.py
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ingestion import ingest
from cleaning import clean, save_clean
from transformation import transform
from feature_engineering import engineer_features
from marts import build_all_marts

logger = logging.getLogger(__name__)


def run() -> None:
    logger.info("=== Superstore Pipeline START ===")

    df = ingest()
    df = clean(df)
    save_clean(df)
    df = transform(df)
    df = engineer_features(df)
    build_all_marts(df)

    logger.info("=== Superstore Pipeline COMPLETE ===")


if __name__ == "__main__":
    run()
