"""
load_source.py
--------------
Loads the raw CSV into a DuckDB file so dbt-duckdb can reference it as a source.
Run this before `dbt run`.

Usage:
    python dbt/load_source.py
"""

from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "Sample_Superstore.csv"
DB_PATH = Path(__file__).resolve().parent / "superstore.duckdb"


def load() -> None:
    """Read raw CSV with pandas and write it into a DuckDB table."""
    print(f"Loading {RAW_CSV} ...")
    df = pd.read_csv(RAW_CSV, encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS raw_superstore")
    con.register("_tmp", df)
    con.execute("CREATE TABLE raw_superstore AS SELECT * FROM _tmp")
    row_count = con.execute("SELECT count(*) FROM raw_superstore").fetchone()[0]
    con.close()

    print(f"Wrote {row_count:,} rows to {DB_PATH}")


if __name__ == "__main__":
    load()
