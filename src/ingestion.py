"""
ingestion.py
------------
Responsible for loading raw data into the pipeline.
Handles encoding detection, basic type casting, and schema validation.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


RAW_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "Sample_Superstore.csv"

EXPECTED_COLUMNS = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Customer Name", "Segment", "Country", "City",
    "State", "Postal Code", "Region", "Product ID", "Category",
    "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit"
]


def load_raw_data(filepath: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Load the raw Superstore CSV file.

    Parameters
    ----------
    filepath : Path
        Path to the raw CSV file.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame as loaded from disk, with no transformations applied.
    """
    logger.info(f"Loading raw data from: {filepath}")

    if not filepath.exists():
        raise FileNotFoundError(f"Raw data file not found at: {filepath}")

    df = pd.read_csv(filepath, encoding="latin1")
    logger.info(f"Loaded {len(df):,} rows and {df.shape[1]} columns.")
    return df


def validate_schema(df: pd.DataFrame) -> bool:
    """
    Validate that the DataFrame contains all expected columns.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to validate.

    Returns
    -------
    bool
        True if schema is valid, raises ValueError otherwise.
    """
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Schema validation failed. Missing columns: {missing}")
    logger.info("Schema validation passed. All expected columns present.")
    return True


def ingest(filepath: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Full ingestion pipeline: load and validate raw data.

    Parameters
    ----------
    filepath : Path
        Path to the raw CSV file.

    Returns
    -------
    pd.DataFrame
        Validated raw DataFrame ready for cleaning.
    """
    df = load_raw_data(filepath)
    validate_schema(df)
    return df


if __name__ == "__main__":
    df = ingest()
    print(df.head())
