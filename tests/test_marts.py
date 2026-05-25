"""Tests for data mart construction — schema and aggregation integrity."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from marts import (
    build_sales_performance_mart,
    build_profitability_mart,
    build_customer_segment_mart,
    build_regional_performance_mart,
    build_discount_impact_mart,
    build_all_marts,
)


class TestSalesPerformanceMart:
    """Verify sales performance mart structure and aggregation."""

    def test_required_columns(self, engineered_df):
        mart = build_sales_performance_mart(engineered_df)
        expected = {"Order Year", "Order Month", "Year-Month",
                    "Total_Sales", "Total_Profit", "Total_Orders",
                    "Total_Units", "Avg_Order_Value", "Profit_Margin_%"}
        assert expected.issubset(set(mart.columns))

    def test_total_sales_match(self, engineered_df):
        mart = build_sales_performance_mart(engineered_df)
        assert abs(mart["Total_Sales"].sum() - engineered_df["Sales"].sum()) < 0.01

    def test_sorted_by_time(self, engineered_df):
        mart = build_sales_performance_mart(engineered_df)
        years = mart["Order Year"].tolist()
        assert years == sorted(years)


class TestProfitabilityMart:
    """Verify profitability mart structure."""

    def test_required_columns(self, engineered_df):
        mart = build_profitability_mart(engineered_df)
        expected = {"Category", "Sub-Category", "Product Name",
                    "Total_Sales", "Total_Profit", "Profit_Margin_%"}
        assert expected.issubset(set(mart.columns))

    def test_loss_rate_range(self, engineered_df):
        mart = build_profitability_mart(engineered_df)
        assert (mart["Loss_Rate_%"] >= 0).all()
        assert (mart["Loss_Rate_%"] <= 100).all()


class TestCustomerSegmentMart:
    """Verify customer segment mart structure."""

    def test_all_segments_present(self, engineered_df):
        mart = build_customer_segment_mart(engineered_df)
        assert set(mart["Segment"]) == {"Consumer", "Corporate"}

    def test_required_columns(self, engineered_df):
        mart = build_customer_segment_mart(engineered_df)
        expected = {"Segment", "Total_Sales", "Total_Profit",
                    "Total_Customers", "Profit_Margin_%"}
        assert expected.issubset(set(mart.columns))


class TestRegionalPerformanceMart:
    """Verify regional performance mart structure."""

    def test_required_columns(self, engineered_df):
        mart = build_regional_performance_mart(engineered_df)
        expected = {"Region", "State", "Total_Sales", "Total_Profit",
                    "Profit_Margin_%"}
        assert expected.issubset(set(mart.columns))

    def test_total_profit_match(self, engineered_df):
        mart = build_regional_performance_mart(engineered_df)
        assert abs(mart["Total_Profit"].sum() - engineered_df["Profit"].sum()) < 0.01


class TestDiscountImpactMart:
    """Verify discount impact mart structure."""

    def test_required_columns(self, engineered_df):
        mart = build_discount_impact_mart(engineered_df)
        expected = {"Discount Band", "Category", "Total_Sales",
                    "Total_Profit", "Profit_Margin_%"}
        assert expected.issubset(set(mart.columns))


class TestBuildAllMarts:
    """Verify the mart orchestrator."""

    def test_returns_five_marts(self, engineered_df):
        result = build_all_marts(engineered_df)
        assert len(result) == 5

    def test_all_mart_keys(self, engineered_df):
        result = build_all_marts(engineered_df)
        expected_keys = {"sales_performance", "profitability",
                         "customer_segment", "regional_performance",
                         "discount_impact"}
        assert set(result.keys()) == expected_keys

    def test_all_marts_are_dataframes(self, engineered_df):
        result = build_all_marts(engineered_df)
        for name, mart in result.items():
            assert isinstance(mart, pd.DataFrame), f"{name} is not a DataFrame"
