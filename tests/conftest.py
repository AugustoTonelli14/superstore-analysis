"""
Shared pytest fixtures for all test modules.
Provides sample DataFrames that mirror the Superstore schema at each
pipeline stage, so tests run fast without touching disk.
"""

import pandas as pd
import numpy as np
import pytest


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Minimal raw DataFrame matching the Superstore schema."""
    return pd.DataFrame({
        "Row ID":       [1, 2, 3, 4, 5],
        "Order ID":     ["CA-2017-001", "CA-2017-001", "CA-2017-002", "CA-2017-003", "CA-2017-003"],
        "Order Date":   ["1/15/2017", "1/15/2017", "3/20/2017", "6/10/2016", "6/10/2016"],
        "Ship Date":    ["1/19/2017", "1/19/2017", "3/24/2017", "6/14/2016", "6/14/2016"],
        "Ship Mode":    ["Standard Class", "Standard Class", "Second Class", "First Class", "First Class"],
        "Customer ID":  ["CG-12520", "CG-12520", "DV-13045", "SO-20335", "SO-20335"],
        "Customer Name":["Claire Gute", "Claire Gute", "Darrin Van Huff", "Sean O'Donnell", "Sean O'Donnell"],
        "Segment":      ["Consumer", "Consumer", "Corporate", "Consumer", "Consumer"],
        "Country":      ["United States"] * 5,
        "City":         ["Henderson", "Henderson", "Los Angeles", "Fort Lauderdale", "Fort Lauderdale"],
        "State":        ["Kentucky", "Kentucky", "California", "Florida", "Florida"],
        "Postal Code":  [42420, 42420, 90036, 33311, 33311],
        "Region":       ["South", "South", "West", "South", "South"],
        "Product ID":   ["FUR-BO-10001798", "FUR-CH-10000454", "OFF-LA-10000240", "FUR-TA-10000577", "OFF-ST-10000760"],
        "Category":     ["Furniture", "Furniture", "Office Supplies", "Furniture", "Office Supplies"],
        "Sub-Category": ["Bookcases", "Chairs", "Labels", "Tables", "Storage"],
        "Product Name": ["Bush Somerset Bookcase", "Hon Deluxe Chair", "Avery Labels", "Bretford Table", "Eldon Storage"],
        "Sales":        [261.96, 731.94, 14.62, 957.58, 22.37],
        "Quantity":     [2, 3, 2, 5, 2],
        "Discount":     [0.0, 0.0, 0.0, 0.45, 0.20],
        "Profit":       [41.91, 219.58, 6.87, -383.03, 0.56],
    })


@pytest.fixture
def raw_df_with_dupes(raw_df) -> pd.DataFrame:
    """Raw DataFrame with two duplicate rows appended."""
    return pd.concat([raw_df, raw_df.iloc[:2]], ignore_index=True)


@pytest.fixture
def cleaned_df(raw_df) -> pd.DataFrame:
    """DataFrame after the cleaning stage (parsed dates, stripped strings)."""
    df = raw_df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
    return df


@pytest.fixture
def transformed_df(cleaned_df) -> pd.DataFrame:
    """DataFrame after the transformation stage."""
    df = cleaned_df.copy()
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Year-Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["Shipping Lead Time"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df


@pytest.fixture
def engineered_df(transformed_df) -> pd.DataFrame:
    """DataFrame after the full feature engineering stage."""
    df = transformed_df.copy()
    df["Profit Margin %"] = np.where(df["Sales"] != 0, (df["Profit"] / df["Sales"]) * 100, 0.0)
    bins = [-0.001, 0.0, 0.199, 0.299, 1.0]
    labels = ["No Discount", "Low (1-19%)", "Medium (20-29%)", "High (30%+)"]
    df["Discount Band"] = pd.cut(df["Discount"], bins=bins, labels=labels)
    df["Loss Flag"] = (df["Profit"] < 0).astype(int)
    df["High Discount Flag"] = (df["Discount"] >= 0.30).astype(int)
    df["Revenue per Unit"] = np.where(df["Quantity"] > 0, df["Sales"] / df["Quantity"], 0.0)
    df["Profit per Unit"] = np.where(df["Quantity"] > 0, df["Profit"] / df["Quantity"], 0.0)
    return df
