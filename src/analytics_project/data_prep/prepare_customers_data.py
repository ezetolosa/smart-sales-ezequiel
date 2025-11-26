"""
analytics_project/data_prep/prepare_customers_data.py

Clean customers_data.csv and write customers_data_prepared.csv.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers
- Ensure consistent formatting
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from analytics_project.utils_logger import logger, project_root

# -------------------------------------------------
# Paths
# -------------------------------------------------
DATA_DIR: Path = project_root / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: Path = DATA_DIR / "prepared"

DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def read_raw_data(file_name: str) -> pd.DataFrame:
    """Read raw customers CSV from data/raw."""
    file_path = RAW_DATA_DIR / file_name
    logger.info(f"READING raw customers from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded customers raw shape={df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"Customers file not found: {file_path}")
        return pd.DataFrame()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Error reading customers file {file_path}: {exc}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    """Write cleaned customers CSV to data/prepared."""
    file_path = PREPARED_DATA_DIR / file_name
    logger.info(f"WRITING prepared customers to: {file_path} shape={df.shape}")
    df.to_csv(file_path, index=False)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows (all columns)."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info(f"remove_duplicates: {before} -> {after} rows")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values.

    Generic strategy:
    - Drop rows that are completely empty.
    """
    missing_before = int(df.isna().sum().sum())
    logger.info(f"Total missing values BEFORE handling: {missing_before}")

    # Drop rows where all columns are NaN
    df = df.dropna(how="all")

    missing_after = int(df.isna().sum().sum())
    logger.info(f"Total missing values AFTER handling: {missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers using IQR for all numeric columns.

    This is generic – it will mainly affect any extra numeric columns
    you added in D3.1 where you intentionally created extreme values.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        logger.info("No numeric columns – skipping outlier removal.")
        return df

    initial_count = len(df)
    logger.info(f"remove_outliers: numeric columns={numeric_cols}")

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            # All values are the same – nothing to trim
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        before_col = len(df)
        df = df[(df[col] >= lower) & (df[col] <= upper)]
        after_col = len(df)
        logger.info(
            f"Outlier filter on {col}: bounds=({lower:.2f}, {upper:.2f}) "
            f"rows {before_col} -> {after_col}",
        )

    logger.info(f"remove_outliers: total rows {initial_count} -> {len(df)}")
    return df


# -------------------------------------------------
# Main
# -------------------------------------------------
def main() -> None:
    logger.info("=====================================")
    logger.info("STARTING prepare_customers_data.py")
    logger.info("=====================================")

    logger.info(f"project_root : {project_root}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")

    input_file = "customers_data.csv"
    output_file = "customers_data_prepared.csv"

    df_raw = read_raw_data(input_file)
    if df_raw.empty:
        logger.error("No customers data loaded. Aborting.")
        return

    original_shape = df_raw.shape
    logger.info(f"Initial customers shape: {original_shape}")
    logger.info(f"Initial customers columns: {list(df_raw.columns)}")

    # Clean column names (strip spaces)
    df = df_raw.copy()
    df.columns = df.columns.str.strip()

    # Pipeline
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = remove_outliers(df)

    save_prepared_data(df, output_file)

    logger.info(f"Original customers shape:  {original_shape}")
    logger.info(f"Prepared customers shape:  {df.shape}")
    logger.info("FINISHED prepare_customers_data.py")
    logger.info("=====================================")


if __name__ == "__main__":
    main()
