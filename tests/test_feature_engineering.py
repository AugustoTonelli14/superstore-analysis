"""Tests for feature engineering — business metrics and flags."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from feature_engineering import (
    add_discount_band,
    add_high_discount_flag,
    add_loss_flag,
    add_profit_margin,
    add_profit_per_unit,
    add_revenue_per_unit,
)


class TestProfitMargin:
    """Verify profit margin calculation."""

    def test_margin_formula(self, cleaned_df):
        result = add_profit_margin(cleaned_df)
        # Row 0: profit=41.91, sales=261.96 -> margin = 16.0%
        expected = (41.91 / 261.96) * 100
        assert abs(result.iloc[0]["Profit Margin %"] - expected) < 0.01

    def test_zero_sales_returns_zero_margin(self, cleaned_df):
        df = cleaned_df.copy()
        df.loc[0, "Sales"] = 0
        result = add_profit_margin(df)
        assert result.iloc[0]["Profit Margin %"] == 0.0

    def test_negative_margin_for_loss(self, cleaned_df):
        result = add_profit_margin(cleaned_df)
        # Row 3 has negative profit
        assert result.iloc[3]["Profit Margin %"] < 0


class TestDiscountBand:
    """Verify discount banding logic."""

    def test_no_discount_band(self, cleaned_df):
        result = add_discount_band(cleaned_df)
        # Row 0 has Discount=0.0
        assert str(result.iloc[0]["Discount Band"]) == "No Discount"

    def test_high_discount_band(self, cleaned_df):
        result = add_discount_band(cleaned_df)
        # Row 3 has Discount=0.45
        assert str(result.iloc[3]["Discount Band"]) == "High (30%+)"

    def test_medium_discount_band(self, cleaned_df):
        result = add_discount_band(cleaned_df)
        # Row 4 has Discount=0.20
        assert "Medium" in str(result.iloc[4]["Discount Band"])

    def test_all_rows_have_band(self, cleaned_df):
        result = add_discount_band(cleaned_df)
        assert result["Discount Band"].isnull().sum() == 0


class TestLossFlag:
    """Verify loss flag binary indicator."""

    def test_loss_flag_on_negative_profit(self, cleaned_df):
        result = add_loss_flag(cleaned_df)
        # Row 3 has profit=-383.03
        assert result.iloc[3]["Loss Flag"] == 1

    def test_no_loss_flag_on_positive_profit(self, cleaned_df):
        result = add_loss_flag(cleaned_df)
        # Row 0 has profit=41.91
        assert result.iloc[0]["Loss Flag"] == 0

    def test_loss_flag_is_binary(self, cleaned_df):
        result = add_loss_flag(cleaned_df)
        assert set(result["Loss Flag"].unique()).issubset({0, 1})


class TestHighDiscountFlag:
    """Verify high discount flag threshold at 30%."""

    def test_high_discount_flagged(self, cleaned_df):
        result = add_high_discount_flag(cleaned_df)
        # Row 3 has Discount=0.45
        assert result.iloc[3]["High Discount Flag"] == 1

    def test_low_discount_not_flagged(self, cleaned_df):
        result = add_high_discount_flag(cleaned_df)
        # Row 0 has Discount=0.0
        assert result.iloc[0]["High Discount Flag"] == 0

    def test_flag_is_binary(self, cleaned_df):
        result = add_high_discount_flag(cleaned_df)
        assert set(result["High Discount Flag"].unique()).issubset({0, 1})


class TestRevenuePerUnit:
    """Verify revenue per unit calculation."""

    def test_revenue_per_unit_formula(self, cleaned_df):
        result = add_revenue_per_unit(cleaned_df)
        # Row 0: sales=261.96, qty=2 -> 130.98
        expected = 261.96 / 2
        assert abs(result.iloc[0]["Revenue per Unit"] - expected) < 0.01

    def test_zero_quantity_returns_zero(self, cleaned_df):
        df = cleaned_df.copy()
        df.loc[0, "Quantity"] = 0
        result = add_revenue_per_unit(df)
        assert result.iloc[0]["Revenue per Unit"] == 0.0


class TestProfitPerUnit:
    """Verify profit per unit calculation."""

    def test_profit_per_unit_formula(self, cleaned_df):
        result = add_profit_per_unit(cleaned_df)
        # Row 0: profit=41.91, qty=2 -> 20.955
        expected = 41.91 / 2
        assert abs(result.iloc[0]["Profit per Unit"] - expected) < 0.01

    def test_negative_profit_per_unit(self, cleaned_df):
        result = add_profit_per_unit(cleaned_df)
        # Row 3 has negative profit
        assert result.iloc[3]["Profit per Unit"] < 0
