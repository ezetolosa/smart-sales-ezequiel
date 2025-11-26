"""data_scrubber.py.

Reusable utility class for performing common data cleaning and
preparation tasks on a pandas DataFrame.
"""

import io
import pandas as pd


class DataScrubber:
    """A utility class for performing common data cleaning and preparation tasks on pandas DataFrames."""

    def __init__(self, df: pd.DataFrame):
        """Initialize the DataScrubber with a DataFrame."""
        self.df = df

    # -------------------------------------------------
    # CONSISTENCY CHECKS
    # -------------------------------------------------
    def check_data_consistency_before_cleaning(self) -> dict[str, pd.Series | int]:
        """Check data consistency before cleaning by calculating counts of null and duplicate entries."""
        null_counts = self.df.isnull().sum()
        duplicate_count = self.df.duplicated().sum()
        return {"null_counts": null_counts, "duplicate_count": duplicate_count}

    def check_data_consistency_after_cleaning(self) -> dict[str, pd.Series | int]:
        """Check data consistency after cleaning to ensure there are no null or duplicate entries."""
        null_counts = self.df.isnull().sum()
        duplicate_count = self.df.duplicated().sum()
        assert null_counts.sum() == 0, "Data still contains null values after cleaning."
        assert duplicate_count == 0, "Data still contains duplicate records after cleaning."
        return {"null_counts": null_counts, "duplicate_count": duplicate_count}

    # -------------------------------------------------
    # DATA TYPE HANDLING
    # -------------------------------------------------
    def convert_column_to_new_data_type(self, column: str, new_type: type) -> pd.DataFrame:
        """Convert a specified column to a new data type."""
        try:
            self.df[column] = self.df[column].astype(new_type)
            return self.df
        except KeyError as exc:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from exc

    # -------------------------------------------------
    # COLUMN MANIPULATION
    # -------------------------------------------------
    def drop_columns(self, columns: list[str]) -> pd.DataFrame:
        """Drop specified columns from the DataFrame."""
        for column in columns:
            if column not in self.df.columns:
                raise ValueError(f"Column name '{column}' not found in the DataFrame.")
        self.df = self.df.drop(columns=columns)
        return self.df

    # -------------------------------------------------
    # OUTLIER FILTERING
    # -------------------------------------------------
    def filter_column_outliers(
        self, column: str, lower_bound: float | int, upper_bound: float | int
    ) -> pd.DataFrame:
        """Filter outliers in a specified column based on lower and upper bounds."""
        try:
            self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
            return self.df
        except KeyError as exc:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from exc

    # -------------------------------------------------
    # STRING FORMATTING
    # -------------------------------------------------
    def format_column_strings_to_lower_and_trim(self, column: str) -> pd.DataFrame:
        """Format strings in a specified column by converting to lowercase and trimming whitespace."""
        try:
            self.df[column] = self.df[column].str.lower().str.strip()
            return self.df
        except KeyError as exc:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from exc

    def format_column_strings_to_upper_and_trim(self, column: str) -> pd.DataFrame:
        """Format strings in a specified column by converting to uppercase and trimming whitespace."""
        try:
            self.df[column] = self.df[column].str.upper().str.strip()
            return self.df
        except KeyError as exc:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from exc

    # -------------------------------------------------
    # MISSING DATA HANDLING
    # -------------------------------------------------
    def handle_missing_data(
        self, drop: bool = False, fill_value: None | float | int | str = None
    ) -> pd.DataFrame:
        """Handle missing data in the DataFrame."""
        if drop:
            self.df = self.df.dropna()
        elif fill_value is not None:
            self.df = self.df.fillna(fill_value)
        return self.df

    # -------------------------------------------------
    # INSPECTION
    # -------------------------------------------------
    def inspect_data(self) -> tuple[str, str]:
        """Inspect the data by providing DataFrame information and summary statistics."""
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()
        describe_str = self.df.describe().to_string()
        return info_str, describe_str

    # -------------------------------------------------
    # DATE PARSING
    # -------------------------------------------------
    def parse_dates_to_add_standard_datetime(self, column: str) -> pd.DataFrame:
        """Parse column into datetime with coercion so invalid dates NEVER break the pipeline."""
        try:
            self.df["StandardDateTime"] = pd.to_datetime(
                self.df[column],
                errors="coerce",  # ← KEY FIX: invalid dates → NaT
                format="mixed",  # ← tries to detect date format automatically
            )
            return self.df
        except KeyError as exc:
            raise ValueError(f"Column name '{column}' not found in the DataFrame.") from exc

    # -------------------------------------------------
    # DUPLICATES
    # -------------------------------------------------
    def remove_duplicate_records(self) -> pd.DataFrame:
        """Remove duplicate rows from the DataFrame."""
        self.df = self.df.drop_duplicates()
        return self.df

    # -------------------------------------------------
    # RENAME + REORDER
    # -------------------------------------------------
    def rename_columns(self, column_mapping: dict[str, str]) -> pd.DataFrame:
        """Rename columns in the DataFrame based on a provided mapping."""
        for old_name, _new_name in column_mapping.items():
            if old_name not in self.df.columns:
                raise ValueError(f"Column '{old_name}' not found in the DataFrame.")
        self.df = self.df.rename(columns=column_mapping)
        return self.df

    def reorder_columns(self, columns: list[str]) -> pd.DataFrame:
        """Reorder columns in the DataFrame based on the specified order."""
        for column in columns:
            if column not in self.df.columns:
                raise ValueError(f"Column name '{column}' not found in the DataFrame.")
        self.df = self.df[columns]
        return self.df
