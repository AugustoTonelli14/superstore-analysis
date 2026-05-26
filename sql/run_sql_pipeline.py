"""
run_sql_pipeline.py
-------------------
Builds all five analytical data marts using SQL (DuckDB) instead of pandas.
Demonstrates the same business logic as the Python pipeline, written in pure SQL.

Pandas handles the CSV loading (latin1 encoding), then DuckDB takes over
for all analytical queries — showcasing SQL fluency on the same dataset.

Usage:
    python sql/run_sql_pipeline.py
"""

import logging
import sys
from pathlib import Path

import duckdb
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "Sample_Superstore.csv"
QUERIES_DIR = Path(__file__).resolve().parent / "queries"
OUTPUT_DIR = PROJECT_ROOT / "data" / "marts"

MARTS = [
    "sales_performance_mart",
    "profitability_mart",
    "customer_segment_mart",
    "regional_performance_mart",
    "discount_impact_mart",
]


def run() -> None:
    """Execute the full SQL pipeline: load CSV, register in DuckDB, run all mart queries."""
    logger.info("=== SQL Pipeline START ===")

    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Raw data not found: {RAW_CSV}")

    # Load CSV with pandas (handles latin1 encoding reliably)
    logger.info(f"Loading raw data from: {RAW_CSV}")
    superstore = pd.read_csv(RAW_CSV, encoding="latin1")
    superstore["Order Date"] = pd.to_datetime(superstore["Order Date"], format="%m/%d/%Y")
    superstore["Ship Date"] = pd.to_datetime(superstore["Ship Date"], format="%m/%d/%Y")
    logger.info(f"Loaded {len(superstore):,} rows.")

    # Register the DataFrame as a DuckDB virtual table
    con = duckdb.connect(":memory:")
    con.register("superstore", superstore)
    logger.info("DataFrame registered in DuckDB as 'superstore'.")

    # Build each mart from its .sql file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for mart_name in MARTS:
        sql_file = QUERIES_DIR / f"{mart_name}.sql"
        if not sql_file.exists():
            logger.warning(f"Query file not found: {sql_file} — skipping.")
            continue

        query = sql_file.read_text(encoding="utf-8")
        result = con.execute(query).fetchdf()

        output_path = OUTPUT_DIR / f"{mart_name}.csv"
        result.to_csv(output_path, index=False)
        logger.info(f"Mart saved: {output_path}  ({len(result):,} rows)")

    con.close()
    logger.info("=== SQL Pipeline COMPLETE ===")


if __name__ == "__main__":
    run()
