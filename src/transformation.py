"""
transformation.py
-----------------
Creates derived time-based columns used throughout the analysis:
  - Order Year, Month, Quarter
  - Shipping Lead Time (calendar days from order to shipment)
  - Period label for trend visualisations
"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract year, month, quarter, and period label from Order Date.
    These fields power all time-series trend analyses.
    """
    df = df.copy()
    df["Order Year"]    = df["Order Date"].dt.year
    df["Order Month"]   = df["Order Date"].dt.month
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Year-Month"]    = df["Order Date"].dt.to_period("M").astype(str)
    df["Year-Quarter"]  = df["Order Date"].dt.to_period("Q").astype(str)
    logger.info("Time features added: Order Year, Month, Quarter, Year-Month, Year-Quarter.")
    return df


def add_shipping_lead_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Shipping Lead Time as the number of calendar days between
    Order Date and Ship Date.  Negative or zero values are anomalies.
    """
    df = df.copy()
    df["Shipping Lead Time"] = (df["Ship Date"] - df["Order Date"]).dt.days
    anomalies = (df["Shipping Lead Time"] <= 0).sum()
    if anomalies > 0:
        logger.warning(f"Shipping Lead Time <= 0 in {anomalies} rows.")
    logger.info("Shipping Lead Time computed.")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full transformation pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame enriched with time-based and shipping features.
    """
    logger.info("Starting transformation pipeline...")
    df = add_time_features(df)
    df = add_shipping_lead_time(df)
    logger.info(f"Transformation complete. Shape: {df.shape}")
    return df


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingestion import ingest
    from cleaning import clean
    raw = ingest()
    cleaned = clean(raw)
    transformed = transform(cleaned)
    print(transformed[["Order Date", "Order Year", "Order Quarter",
                        "Year-Month", "Shipping Lead Time"]].head())
