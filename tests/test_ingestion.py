"""Tests for the ingestion module — schema validation and data loading."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from ingestion import validate_schema, EXPECTED_COLUMNS


class TestSchemaValidation:
    """Ensure the schema validator catches missing columns."""

    def test_valid_schema_passes(self, raw_df):
        assert validate_schema(raw_df) is True

    def test_missing_column_raises(self, raw_df):
        df = raw_df.drop(columns=["Sales"])
        with pytest.raises(ValueError, match="Missing columns"):
            validate_schema(df)

    def test_extra_columns_still_pass(self, raw_df):
        df = raw_df.copy()
        df["Extra Column"] = 0
        assert validate_schema(df) is True

    def test_expected_columns_count(self):
        assert len(EXPECTED_COLUMNS) == 21


class TestRawDataIntegrity:
    """Validate basic properties of the raw fixture."""

    def test_raw_df_has_correct_shape(self, raw_df):
        assert raw_df.shape == (5, 21)

    def test_no_null_values_in_raw(self, raw_df):
        assert raw_df.isnull().sum().sum() == 0

    def test_sales_are_positive(self, raw_df):
        assert (raw_df["Sales"] > 0).all()

    def test_quantity_is_positive_integer(self, raw_df):
        assert (raw_df["Quantity"] >= 1).all()
