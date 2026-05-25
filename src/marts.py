"""
marts.py
--------
Creates analytical data marts from the fully engineered base dataset.
Each mart is purpose-built to support a specific category of business questions.

Marts produced:
  1. sales_performance_mart   – Revenue trends and volume by time period
  2. profitability_mart       – Margin and profit by category / sub-category / product
  3. customer_segment_mart    – Performance by customer segment
  4. regional_performance_mart – Sales, profit, and margin by region and state
  5. discount_impact_mart     – Profitability breakdown by discount band
"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

MARTS_PATH = Path(__file__).resolve().parent.parent / "data" / "marts"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _save(df: pd.DataFrame, name: str) -> None:
    MARTS_PATH.mkdir(parents=True, exist_ok=True)
    fp = MARTS_PATH / f"{name}.csv"
    df.to_csv(fp, index=False)
    logger.info(f"Mart saved: {fp}  ({len(df):,} rows)")


# ---------------------------------------------------------------------------
# Mart definitions
# ---------------------------------------------------------------------------

def build_sales_performance_mart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly and yearly sales and order volume trends.

    Purpose : Understand revenue trajectory and seasonal patterns.
    Decisions: Budget planning, campaign timing, inventory management.
    """
    mart = (
        df.groupby(["Order Year", "Order Month", "Year-Month"])
        .agg(
            Total_Sales   = ("Sales",    "sum"),
            Total_Profit  = ("Profit",   "sum"),
            Total_Orders  = ("Order ID", "nunique"),
            Total_Units   = ("Quantity", "sum"),
        )
        .reset_index()
        .sort_values(["Order Year", "Order Month"])
    )
    mart["Avg_Order_Value"] = mart["Total_Sales"] / mart["Total_Orders"]
    mart["Profit_Margin_%"] = (mart["Total_Profit"] / mart["Total_Sales"]) * 100
    _save(mart, "sales_performance_mart")
    return mart


def build_profitability_mart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit and margin by category, sub-category, and product.

    Purpose : Identify the most and least profitable areas of the portfolio.
    Decisions: Product rationalisation, pricing adjustments, discount policy.
    """
    mart = (
        df.groupby(["Category", "Sub-Category", "Product Name"])
        .agg(
            Total_Sales      = ("Sales",             "sum"),
            Total_Profit     = ("Profit",            "sum"),
            Total_Units      = ("Quantity",          "sum"),
            Avg_Margin_Pct   = ("Profit Margin %",   "mean"),
            Orders           = ("Order ID",          "nunique"),
            Loss_Orders      = ("Loss Flag",         "sum"),
        )
        .reset_index()
        .sort_values("Total_Profit", ascending=False)
    )
    mart["Profit_Margin_%"] = (mart["Total_Profit"] / mart["Total_Sales"]) * 100
    mart["Loss_Rate_%"]     = (mart["Loss_Orders"] / mart["Orders"]) * 100
    _save(mart, "profitability_mart")
    return mart


def build_customer_segment_mart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sales, profit, and margin by customer segment (Consumer, Corporate, Home Office).

    Purpose : Determine which segments drive value and which represent risk.
    Decisions: Sales force allocation, promotional strategy, retention investment.
    """
    mart = (
        df.groupby("Segment")
        .agg(
            Total_Sales       = ("Sales",           "sum"),
            Total_Profit      = ("Profit",          "sum"),
            Total_Customers   = ("Customer ID",     "nunique"),
            Total_Orders      = ("Order ID",        "nunique"),
            Avg_Discount      = ("Discount",        "mean"),
            Loss_Orders       = ("Loss Flag",       "sum"),
        )
        .reset_index()
    )
    mart["Profit_Margin_%"]     = (mart["Total_Profit"] / mart["Total_Sales"]) * 100
    mart["Avg_Revenue_per_Cust"] = mart["Total_Sales"] / mart["Total_Customers"]
    mart["Loss_Rate_%"]          = (mart["Loss_Orders"] / mart["Total_Orders"]) * 100
    _save(mart, "customer_segment_mart")
    return mart


def build_regional_performance_mart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sales, profit, and margin by region and state.

    Purpose : Identify geographic strengths, weaknesses, and inefficiencies.
    Decisions: Regional resource allocation, territory planning, discount policy.
    """
    mart = (
        df.groupby(["Region", "State"])
        .agg(
            Total_Sales    = ("Sales",    "sum"),
            Total_Profit   = ("Profit",   "sum"),
            Total_Orders   = ("Order ID", "nunique"),
            Avg_Discount   = ("Discount", "mean"),
            Loss_Orders    = ("Loss Flag","sum"),
        )
        .reset_index()
        .sort_values("Total_Profit", ascending=False)
    )
    mart["Profit_Margin_%"] = (mart["Total_Profit"] / mart["Total_Sales"]) * 100
    mart["Loss_Rate_%"]     = (mart["Loss_Orders"] / mart["Total_Orders"]) * 100
    _save(mart, "regional_performance_mart")
    return mart


def build_discount_impact_mart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profitability breakdown by discount band.

    Purpose : Quantify the financial damage caused by aggressive discounting.
    Decisions: Discount policy redesign, approval thresholds, sales incentive structures.
    """
    mart = (
        df.groupby(["Discount Band", "Category"], observed=True)
        .agg(
            Total_Sales    = ("Sales",           "sum"),
            Total_Profit   = ("Profit",          "sum"),
            Orders         = ("Order ID",        "nunique"),
            Loss_Orders    = ("Loss Flag",       "sum"),
            Avg_Discount   = ("Discount",        "mean"),
        )
        .reset_index()
    )
    mart["Profit_Margin_%"] = (mart["Total_Profit"] / mart["Total_Sales"]) * 100
    mart["Loss_Rate_%"]     = (mart["Loss_Orders"] / mart["Orders"]) * 100
    _save(mart, "discount_impact_mart")
    return mart


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def build_all_marts(df: pd.DataFrame) -> dict:
    """
    Build all five analytical data marts.

    Parameters
    ----------
    df : pd.DataFrame
        Fully engineered dataset.

    Returns
    -------
    dict
        Dictionary of mart name -> DataFrame.
    """
    logger.info("Building all analytical data marts...")
    marts = {
        "sales_performance":   build_sales_performance_mart(df),
        "profitability":       build_profitability_mart(df),
        "customer_segment":    build_customer_segment_mart(df),
        "regional_performance": build_regional_performance_mart(df),
        "discount_impact":     build_discount_impact_mart(df),
    }
    logger.info("All marts built successfully.")
    return marts


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingestion import ingest
    from cleaning import clean
    from transformation import transform
    from feature_engineering import engineer_features

    df = engineer_features(transform(clean(ingest())))
    marts = build_all_marts(df)
    for name, mart in marts.items():
        print(f"\n--- {name} ---")
        print(mart.head(3))
