"""
cleaning.py
-----------
Handles all data quality operations:
- Missing value detection and handling
- Duplicate removal
- Type casting and date parsing
- Standardisation of string fields
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "superstore_clean.csv"


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    """Return a Series showing missing value counts per column."""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        logger.info("No missing values detected.")
    else:
        logger.warning(f"Missing values found:\n{missing}")
    return missing


def check_duplicates(df: pd.DataFrame) -> int:
    """Return number of fully duplicated rows."""
    n_dupes = df.duplicated().sum()
    logger.info(f"Duplicate rows found: {n_dupes}")
    return n_dupes


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove fully duplicated rows, retaining first occurrence."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    if before != after:
        logger.info(f"Removed {before - after} duplicate rows.")
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Order Date and Ship Date from string to datetime.
    Handles MM/DD/YYYY format as used in the Superstore dataset.
    """
    df = df.copy()
    for col in ["Order Date", "Ship Date"]:
        df[col] = pd.to_datetime(df[col], format="%m/%d/%Y", errors="coerce")
        n_null = df[col].isnull().sum()
        if n_null > 0:
            logger.warning(f"{col}: {n_null} dates could not be parsed.")
        else:
            logger.info(f"{col}: Parsed successfully.")
    return df


def standardise_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip leading/trailing whitespace from all string columns.
    Ensures consistent lookups when grouping by segment, state, etc.
    """
    df = df.copy()
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    logger.info(f"Standardised string columns: {list(str_cols)}")
    return df


def validate_numeric_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate key numeric columns for physically impossible values.
    Discount must be in [0, 1]. Quantity must be >= 1.
    Rows violating these are flagged but not removed.
    """
    df = df.copy()
    invalid_discount = df[(df["Discount"] < 0) | (df["Discount"] > 1)]
    if not invalid_discount.empty:
        logger.warning(f"{len(invalid_discount)} rows with Discount outside [0, 1].")

    invalid_qty = df[df["Quantity"] < 1]
    if not invalid_qty.empty:
        logger.warning(f"{len(invalid_qty)} rows with Quantity < 1.")

    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline. Steps applied in order:
      1. Remove duplicates
      2. Parse dates
      3. Standardise string fields
      4. Validate numeric ranges

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from ingestion.

    Returns
    -------
    pd.DataFrame
        Clean DataFrame ready for transformation.
    """
    logger.info("Starting data cleaning pipeline...")
    check_missing_values(df)
    check_duplicates(df)

    df = remove_duplicates(df)
    df = parse_dates(df)
    df = standardise_strings(df)
    df = validate_numeric_ranges(df)

    logger.info(f"Cleaning complete. Final shape: {df.shape}")
    return df


def save_clean(df: pd.DataFrame, filepath: Path = PROCESSED_PATH) -> None:
    """Persist the cleaned DataFrame to CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.info(f"Cleaned data saved to: {filepath}")


if __name__ == "__main__":
    from ingestion import ingest
    raw = ingest()
    clean_df = clean(raw)
    save_clean(clean_df)
    print(clean_df.dtypes)
