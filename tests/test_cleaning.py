"""Tests for the cleaning module — deduplication, date parsing, validation."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from cleaning import (
    check_duplicates,
    check_missing_values,
    parse_dates,
    remove_duplicates,
    standardise_strings,
    validate_numeric_ranges,
)


class TestDuplicateRemoval:
    """Verify that duplicate rows are correctly identified and removed."""

    def test_removes_exact_duplicates(self, raw_df_with_dupes):
        result = remove_duplicates(raw_df_with_dupes)
        assert len(result) == 5  # original 5, dupes removed

    def test_no_change_when_no_duplicates(self, raw_df):
        result = remove_duplicates(raw_df)
        assert len(result) == len(raw_df)

    def test_check_duplicates_count(self, raw_df_with_dupes):
        count = check_duplicates(raw_df_with_dupes)
        assert count == 2


class TestDateParsing:
    """Verify date columns are correctly converted to datetime."""

    def test_dates_become_datetime(self, raw_df):
        result = parse_dates(raw_df)
        assert pd.api.types.is_datetime64_any_dtype(result["Order Date"])
        assert pd.api.types.is_datetime64_any_dtype(result["Ship Date"])

    def test_no_null_dates_after_parsing(self, raw_df):
        result = parse_dates(raw_df)
        assert result["Order Date"].isnull().sum() == 0
        assert result["Ship Date"].isnull().sum() == 0

    def test_ship_date_after_order_date(self, raw_df):
        result = parse_dates(raw_df)
        assert (result["Ship Date"] >= result["Order Date"]).all()


class TestStringStandardisation:
    """Verify whitespace is stripped from string columns."""

    def test_strips_whitespace(self, raw_df):
        df = raw_df.copy()
        df.loc[0, "State"] = "  Kentucky  "
        df.loc[1, "City"] = "Henderson   "
        result = standardise_strings(df)
        assert result.loc[0, "State"] == "Kentucky"
        assert result.loc[1, "City"] == "Henderson"

    def test_does_not_modify_non_string_columns(self, raw_df):
        result = standardise_strings(raw_df)
        assert (result["Sales"] == raw_df["Sales"]).all()


class TestNumericValidation:
    """Verify numeric range checks work correctly."""

    def test_valid_data_passes(self, raw_df):
        result = validate_numeric_ranges(raw_df)
        assert len(result) == len(raw_df)

    def test_missing_values_detection(self, raw_df):
        missing = check_missing_values(raw_df)
        assert len(missing) == 0
