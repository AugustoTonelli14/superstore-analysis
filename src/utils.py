"""
utils.py
--------
Shared utility functions used across notebooks and scripts.
Covers reusable summary helpers, formatting, and chart configuration.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import Optional


# ---------------------------------------------------------------------------
# Plot style configuration
# ---------------------------------------------------------------------------

def set_plot_style() -> None:
    """Apply a consistent, clean, professional matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor":   "white",
        "axes.facecolor":     "white",
        "axes.grid":          True,
        "grid.color":         "#e5e5e5",
        "grid.linewidth":     0.8,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.labelsize":     12,
        "axes.titlesize":     13,
        "axes.titleweight":   "bold",
        "xtick.labelsize":    10,
        "ytick.labelsize":    10,
        "legend.fontsize":    10,
        "font.family":        "sans-serif",
    })


PALETTE = {
    "blue":       "#2563EB",
    "green":      "#16A34A",
    "red":        "#DC2626",
    "orange":     "#EA580C",
    "slate":      "#475569",
    "light_blue": "#93C5FD",
    "light_green":"#86EFAC",
    "light_red":  "#FCA5A5",
    "gray":       "#9CA3AF",
}


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------

def kpi_summary(df: pd.DataFrame) -> dict:
    """
    Compute high-level KPIs from the base dataset.

    Returns
    -------
    dict
        Dictionary with total_sales, total_profit, overall_margin_pct,
        total_orders, total_customers, total_products.
    """
    return {
        "total_sales":       round(df["Sales"].sum(), 2),
        "total_profit":      round(df["Profit"].sum(), 2),
        "overall_margin_%":  round((df["Profit"].sum() / df["Sales"].sum()) * 100, 2),
        "total_orders":      df["Order ID"].nunique(),
        "total_customers":   df["Customer ID"].nunique(),
        "total_products":    df["Product ID"].nunique(),
        "loss_orders":       int(df["Loss Flag"].sum()),
        "loss_rate_%":       round((df["Loss Flag"].sum() / len(df)) * 100, 2),
        "avg_discount":      round(df["Discount"].mean() * 100, 2),
    }


def top_n_by(df: pd.DataFrame, group_col: str, value_col: str,
             n: int = 10, ascending: bool = False) -> pd.DataFrame:
    """
    Return the top N rows grouped by group_col, sorted by value_col.

    Parameters
    ----------
    df : pd.DataFrame
    group_col : str   Column to group by.
    value_col : str   Column to aggregate and sort by.
    n : int           Number of rows to return.
    ascending : bool  Sort direction.
    """
    return (
        df.groupby(group_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(value_col, ascending=ascending)
        .head(n)
    )


def profit_margin_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Compute total sales, total profit, and profit margin % by any dimension.
    """
    agg = (
        df.groupby(group_col)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
        .reset_index()
    )
    agg["Profit_Margin_%"] = (agg["Total_Profit"] / agg["Total_Sales"]) * 100
    return agg.sort_values("Profit_Margin_%", ascending=False)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_currency(value: float) -> str:
    """Return a compact USD currency string (e.g. $2.3M, $450K)."""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.0f}"


def add_currency_formatter(ax: plt.Axes, axis: str = "y") -> None:
    """Apply compact currency formatting to x or y axis tick labels."""
    formatter = mticker.FuncFormatter(lambda x, _: fmt_currency(x))
    if axis == "y":
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


def add_value_labels(ax: plt.Axes, fmt: str = "{:.1f}", fontsize: int = 9,
                     padding: float = 3) -> None:
    """
    Annotate bar chart bars with their values.
    Works for both vertical and horizontal bar charts.
    """
    patches = [p for p in ax.patches if p.get_width() != 0 or p.get_height() != 0]
    if not patches:
        return
    # Horizontal bars share a uniform height; vertical bars share a uniform width.
    # Compare variance to determine orientation reliably.
    widths  = [p.get_width()  for p in patches]
    heights = [p.get_height() for p in patches]
    is_horizontal = (max(heights) - min(heights)) < (max(widths) - min(widths))

    for patch in patches:
        w, h = patch.get_width(), patch.get_height()
        x, y = patch.get_xy()
        if is_horizontal:
            ax.annotate(fmt.format(w),
                        (x + w, y + h / 2),
                        ha="left", va="center",
                        fontsize=fontsize,
                        xytext=(padding, 0),
                        textcoords="offset points")
        else:
            ax.annotate(fmt.format(h),
                        (x + w / 2, y + h),
                        ha="center", va="bottom",
                        fontsize=fontsize,
                        xytext=(0, padding),
                        textcoords="offset points")
