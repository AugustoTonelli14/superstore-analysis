"""Tests for the transformation module — time features and shipping lead time."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from transformation import add_shipping_lead_time, add_time_features


class TestTimeFeatures:
    """Verify all time-based columns are correctly derived."""

    def test_year_extraction(self, cleaned_df):
        result = add_time_features(cleaned_df)
        assert "Order Year" in result.columns
        assert set(result["Order Year"].unique()) == {2016, 2017}

    def test_month_extraction(self, cleaned_df):
        result = add_time_features(cleaned_df)
        assert "Order Month" in result.columns
        assert result["Order Month"].between(1, 12).all()

    def test_quarter_extraction(self, cleaned_df):
        result = add_time_features(cleaned_df)
        assert "Order Quarter" in result.columns
        assert result["Order Quarter"].between(1, 4).all()

    def test_year_month_format(self, cleaned_df):
        result = add_time_features(cleaned_df)
        assert "Year-Month" in result.columns
        # Format should be YYYY-MM
        assert all(len(ym) == 7 for ym in result["Year-Month"])

    def test_year_quarter_format(self, cleaned_df):
        result = add_time_features(cleaned_df)
        assert "Year-Quarter" in result.columns

    def test_does_not_modify_original(self, cleaned_df):
        original_cols = list(cleaned_df.columns)
        add_time_features(cleaned_df)
        assert list(cleaned_df.columns) == original_cols


class TestShippingLeadTime:
    """Verify shipping lead time calculation."""

    def test_lead_time_is_positive(self, cleaned_df):
        result = add_shipping_lead_time(cleaned_df)
        assert (result["Shipping Lead Time"] >= 0).all()

    def test_lead_time_values(self, cleaned_df):
        result = add_shipping_lead_time(cleaned_df)
        # Row 0: Jan 15 -> Jan 19 = 4 days
        assert result.iloc[0]["Shipping Lead Time"] == 4

    def test_lead_time_column_exists(self, cleaned_df):
        result = add_shipping_lead_time(cleaned_df)
        assert "Shipping Lead Time" in result.columns
