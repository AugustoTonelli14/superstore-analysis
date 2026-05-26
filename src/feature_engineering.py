"""
feature_engineering.py
-----------------------
Creates analytically meaningful business features from base columns.

Features created:
  - Profit Margin %
  - Discount Band (categorical bucketing of discount levels)
  - Loss Flag (binary: 1 if order line is loss-making)
  - High Discount Flag (binary: 1 if discount >= 0.30)
  - Revenue per Unit (Sales / Quantity)
  - Profit per Unit (Profit / Quantity)

Each feature is documented with its business rationale.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def add_profit_margin(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit Margin = Profit / Sales.

    Rationale: Raw profit hides scale effects. A $50 profit on $100 sales
    (50% margin) is far healthier than the same $50 on $1,000 sales (5% margin).
    Margin normalises across product price points, enabling fair comparisons.
    """
    df = df.copy()
    df["Profit Margin %"] = np.where(
        df["Sales"] != 0,
        (df["Profit"] / df["Sales"]) * 100,
        0.0
    )
    logger.info("Feature added: Profit Margin %")
    return df


def add_discount_band(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorise discount level into four business-meaningful bands:
      - No Discount  : 0%
      - Low          : 1–19%
      - Medium       : 20–29%
      - High         : 30%+

    Rationale: Granular discount values are hard to interpret at a glance.
    Banding allows management to quickly identify high-discount exposure
    and test whether profitability degrades at specific thresholds.
    """
    df = df.copy()
    bins   = [-0.001, 0.0, 0.199, 0.299, 1.0]
    labels = ["No Discount", "Low (1–19%)", "Medium (20–29%)", "High (30%+)"]
    df["Discount Band"] = pd.cut(df["Discount"], bins=bins, labels=labels)
    logger.info("Feature added: Discount Band")
    return df


def add_loss_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Loss Flag = 1 when the order line generates negative profit.

    Rationale: Allows rapid aggregation of loss-making activity by any
    dimension (category, region, customer segment) without filtering.
    """
    df = df.copy()
    df["Loss Flag"] = (df["Profit"] < 0).astype(int)
    logger.info("Feature added: Loss Flag")
    return df


def add_high_discount_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    High Discount Flag = 1 when Discount >= 0.30.

    Rationale: The analysis consistently shows that discounts at or above
    30% are strongly correlated with negative margins. This binary flag
    allows quick cross-tabulation and proportion calculations.
    """
    df = df.copy()
    df["High Discount Flag"] = (df["Discount"] >= 0.30).astype(int)
    logger.info("Feature added: High Discount Flag")
    return df


def add_revenue_per_unit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Revenue per Unit = Sales / Quantity.

    Rationale: Indicates effective selling price per item, reflecting the
    combined impact of list price and applied discounts.
    """
    df = df.copy()
    df["Revenue per Unit"] = np.where(
        df["Quantity"] > 0,
        df["Sales"] / df["Quantity"],
        0.0
    )
    logger.info("Feature added: Revenue per Unit")
    return df


def add_profit_per_unit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit per Unit = Profit / Quantity.

    Rationale: Shows the effective contribution of each unit sold, useful
    for identifying products that sell in volume but generate minimal margin.
    """
    df = df.copy()
    df["Profit per Unit"] = np.where(
        df["Quantity"] > 0,
        df["Profit"] / df["Quantity"],
        0.0
    )
    logger.info("Feature added: Profit per Unit")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full feature engineering pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Transformed DataFrame with time-based features.

    Returns
    -------
    pd.DataFrame
        DataFrame with all business features appended.
    """
    logger.info("Starting feature engineering pipeline...")
    df = add_profit_margin(df)
    df = add_discount_band(df)
    df = add_loss_flag(df)
    df = add_high_discount_flag(df)
    df = add_revenue_per_unit(df)
    df = add_profit_per_unit(df)
    logger.info(f"Feature engineering complete. Shape: {df.shape}")
    return df


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cleaning import clean
    from ingestion import ingest
    from transformation import transform

    raw        = ingest()
    cleaned    = clean(raw)
    transformed = transform(cleaned)
    featured   = engineer_features(transformed)
    print(featured[["Sales", "Profit", "Discount", "Profit Margin %",
                     "Discount Band", "Loss Flag", "High Discount Flag"]].head(10))
