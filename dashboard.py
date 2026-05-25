"""
dashboard.py
------------
Interactive Streamlit dashboard for the Superstore analysis.
Provides real-time filtering and exploration of KPIs, trends,
profitability, and geographic performance.

Usage:
    streamlit run dashboard.py
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── project imports ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from ingestion import ingest
from cleaning import clean
from transformation import transform
from feature_engineering import engineer_features
from utils import set_plot_style, PALETTE, fmt_currency, add_currency_formatter

# ── page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

set_plot_style()


# ── data loading (cached) ───────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Run the full pipeline and cache the result."""
    df = engineer_features(transform(clean(ingest())))
    return df


df_full = load_data()

# ── sidebar filters ──────────────────────────────────────────────────
st.sidebar.title("Filters")

years = sorted(df_full["Order Year"].unique())
selected_years = st.sidebar.multiselect("Year", years, default=years)

categories = sorted(df_full["Category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

regions = sorted(df_full["Region"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

segments = sorted(df_full["Segment"].unique())
selected_segments = st.sidebar.multiselect("Segment", segments, default=segments)

# apply filters
df = df_full[
    (df_full["Order Year"].isin(selected_years))
    & (df_full["Category"].isin(selected_categories))
    & (df_full["Region"].isin(selected_regions))
    & (df_full["Segment"].isin(selected_segments))
]

# ── header ───────────────────────────────────────────────────────────
st.title("Superstore Executive Dashboard")
st.caption(f"Showing **{len(df):,}** order lines of {len(df_full):,} total  |  "
           f"Filters: {len(selected_years)} years, {len(selected_categories)} categories, "
           f"{len(selected_regions)} regions, {len(selected_segments)} segments")

st.divider()

# =====================================================================
# SECTION 1 — KPI CARDS
# =====================================================================

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
margin_pct = (total_profit / total_sales * 100) if total_sales else 0
total_orders = df["Order ID"].nunique()
total_customers = df["Customer ID"].nunique()
loss_rate = (df["Loss Flag"].sum() / len(df) * 100) if len(df) else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Revenue", fmt_currency(total_sales))
col2.metric("Profit", fmt_currency(total_profit))
col3.metric("Margin", f"{margin_pct:.1f}%")
col4.metric("Orders", f"{total_orders:,}")
col5.metric("Customers", f"{total_customers:,}")
col6.metric("Loss Rate", f"{loss_rate:.1f}%")

st.divider()

# =====================================================================
# SECTION 2 — REVENUE & PROFIT TRENDS
# =====================================================================

st.subheader("Revenue & Profit Trends")

monthly = (
    df.groupby("Year-Month")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
    .sort_values("Year-Month")
)
monthly["Margin_%"] = monthly["Profit"] / monthly["Sales"] * 100

col_left, col_right = st.columns(2)

with col_left:
    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(monthly))
    ax.fill_between(x, monthly["Sales"], alpha=0.25, color=PALETTE["blue"])
    ax.plot(x, monthly["Sales"], color=PALETTE["blue"], linewidth=1.8, label="Revenue")
    ax.plot(x, monthly["Profit"], color=PALETTE["green"], linewidth=1.5, label="Profit")
    tick_pos = [i for i, ym in enumerate(monthly["Year-Month"]) if ym.endswith("-01")]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([monthly["Year-Month"].iloc[i] for i in tick_pos], rotation=45, ha="right")
    add_currency_formatter(ax)
    ax.set_title("Monthly Revenue & Profit")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE["green"] if m >= 0 else PALETTE["red"] for m in monthly["Margin_%"]]
    ax.bar(range(len(monthly)), monthly["Margin_%"], color=colors, alpha=0.8, width=0.9)
    avg_margin = monthly["Margin_%"].mean()
    ax.axhline(avg_margin, color=PALETTE["slate"], linestyle="--", linewidth=1,
               label=f"Avg {avg_margin:.1f}%")
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([monthly["Year-Month"].iloc[i] for i in tick_pos], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_title("Monthly Profit Margin %")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# =====================================================================
# SECTION 3 — CATEGORY & SUB-CATEGORY PROFITABILITY
# =====================================================================

st.subheader("Category & Sub-Category Profitability")

col_left, col_right = st.columns(2)

with col_left:
    cat_perf = (
        df.groupby("Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .assign(**{"Margin_%": lambda x: x["Profit"] / x["Sales"] * 100})
        .reset_index()
        .sort_values("Profit", ascending=True)
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE["green"] if p >= 0 else PALETTE["red"] for p in cat_perf["Profit"]]
    bars = ax.barh(cat_perf["Category"], cat_perf["Profit"], color=colors, alpha=0.85)
    for bar, margin in zip(bars, cat_perf["Margin_%"]):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                f"{margin:.1f}%", va="center", fontsize=9)
    add_currency_formatter(ax, axis="x")
    ax.set_title("Total Profit by Category")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_right:
    subcat_perf = (
        df.groupby("Sub-Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .assign(**{"Margin_%": lambda x: x["Profit"] / x["Sales"] * 100})
        .reset_index()
        .sort_values("Profit")
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [PALETTE["red"] if p < 0 else PALETTE["green"] for p in subcat_perf["Profit"]]
    ax.barh(subcat_perf["Sub-Category"], subcat_perf["Profit"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    add_currency_formatter(ax, axis="x")
    ax.set_title("Profit by Sub-Category")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# =====================================================================
# SECTION 4 — DISCOUNT IMPACT
# =====================================================================

st.subheader("Discount Impact Analysis")

col_left, col_right = st.columns(2)

with col_left:
    disc_summary = (
        df.groupby("Discount Band", observed=True)
        .agg(Total_Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"),
             Loss_Orders=("Loss Flag", "sum"))
        .reset_index()
    )
    disc_summary["Loss_Rate_%"] = disc_summary["Loss_Orders"] / disc_summary["Orders"] * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    bands = disc_summary["Discount Band"].astype(str)
    colors = [PALETTE["green"] if p >= 0 else PALETTE["red"] for p in disc_summary["Total_Profit"]]
    ax.bar(bands, disc_summary["Total_Profit"], color=colors, alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.8)
    add_currency_formatter(ax)
    ax.set_title("Total Profit by Discount Band")
    for i, (p, lr) in enumerate(zip(disc_summary["Total_Profit"], disc_summary["Loss_Rate_%"])):
        y_off = 2000 if p >= 0 else -8000
        ax.text(i, p + y_off, f"Loss: {lr:.0f}%", ha="center", fontsize=8)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(8, 4))
    sample = df.sample(min(3000, len(df)), random_state=42) if len(df) > 0 else df
    colors = [PALETTE["green"] if m >= 0 else PALETTE["red"] for m in sample["Profit Margin %"]]
    ax.scatter(sample["Discount"], sample["Profit Margin %"], c=colors, alpha=0.3, s=12)
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.axvline(0.30, color=PALETTE["orange"], linewidth=1.5, linestyle="--", label="30% threshold")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("Discount Rate")
    ax.set_ylabel("Profit Margin %")
    ax.set_title("Discount vs Profit Margin")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# =====================================================================
# SECTION 5 — REGIONAL PERFORMANCE
# =====================================================================

st.subheader("Regional & State Performance")

col_left, col_right = st.columns(2)

with col_left:
    region_perf = (
        df.groupby("Region")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .assign(**{"Margin_%": lambda x: x["Profit"] / x["Sales"] * 100})
        .reset_index()
        .sort_values("Profit")
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE["green"] if m >= margin_pct else PALETTE["orange"] for m in region_perf["Margin_%"]]
    bars = ax.barh(region_perf["Region"], region_perf["Profit"], color=colors, alpha=0.85)
    for bar, margin in zip(bars, region_perf["Margin_%"]):
        ax.text(bar.get_width() + 300, bar.get_y() + bar.get_height() / 2,
                f"{margin:.1f}%", va="center", fontsize=9)
    add_currency_formatter(ax, axis="x")
    ax.set_title("Profit by Region (label = margin %)")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_right:
    state_perf = (
        df.groupby("State")
        .agg(Profit=("Profit", "sum"))
        .reset_index()
        .sort_values("Profit")
    )
    worst10 = state_perf.head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE["red"] if p < 0 else PALETTE["green"] for p in worst10["Profit"]]
    ax.barh(worst10["State"], worst10["Profit"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    add_currency_formatter(ax, axis="x")
    ax.set_title("10 Worst-Performing States")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# =====================================================================
# SECTION 6 — DATA TABLE
# =====================================================================

st.subheader("Explore the Data")

show_cols = ["Order ID", "Order Date", "Category", "Sub-Category", "Product Name",
             "Segment", "Region", "State", "Sales", "Profit", "Discount",
             "Profit Margin %", "Discount Band", "Loss Flag"]
available = [c for c in show_cols if c in df.columns]

st.dataframe(
    df[available].sort_values("Order Date", ascending=False).head(500),
    use_container_width=True,
    hide_index=True,
)

# ── footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("Superstore Executive Dashboard | Built with Streamlit + matplotlib | "
           "Data: Sample Superstore 2014-2017")
