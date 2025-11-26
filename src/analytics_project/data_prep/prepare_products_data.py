"""
analytics_project/data_prep/prepare_products_data.py

Clean products_data.csv and write products_data_prepared.csv.

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

DATA_DIR: Path = project_root / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: Path = DATA_DIR / "prepared"

DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)


def read_raw_data(file_name: str) -> pd.DataFrame:
    file_path = RAW_DATA_DIR / file_name
    logger.info(f"READING raw products from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded products raw shape={df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"Products file not found: {file_path}")
        return pd.DataFrame()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Error reading products file {file_path}: {exc}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    file_path = PREPARED_DATA_DIR / file_name
    logger.info(f"WRITING prepared products to: {file_path} shape={df.shape}")
    df.to_csv(file_path, index=False)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows (all columns)."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info(f"remove_duplicates (products): {before} -> {after} rows")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Generic missing value handling for products."""
    missing_before = df.isna().sum()
    logger.info(f"Missing values by column BEFORE:\n{missing_before}")

    # Drop rows that are completely blank
    df = df.dropna(how="all")

    missing_after = df.isna().sum()
    logger.info(f"Missing values by column AFTER:\n{missing_after}")
    logger.info(f"{len(df)} product records remaining after missing handling.")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers using IQR for numeric columns
    (e.g. price, stock_quantity, discount_percent, etc.).
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        logger.info("No numeric columns – skipping outlier removal for products.")
        return df

    initial_count = len(df)
    logger.info(f"remove_outliers (products): numeric columns={numeric_cols}")

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
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

    logger.info(f"remove_outliers (products): total rows {initial_count} -> {len(df)}")
    return df


def standardize_formats(df: pd.DataFrame) -> pd.DataFrame:
    """Basic formatting for products – column names, text normalization, etc."""
    logger.info("standardize_formats (products) starting")

    # Example: make column names snake_case
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    changed = [f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new]
    if changed:
        logger.info(f"Column name changes: {changed}")

    return df


def main() -> None:
    logger.info("=====================================")
    logger.info("STARTING prepare_products_data.py")
    logger.info("=====================================")

    logger.info(f"project_root : {project_root}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")

    input_file = "products_data.csv"
    output_file = "products_data_prepared.csv"

    df_raw = read_raw_data(input_file)
    if df_raw.empty:
        logger.error("No products data loaded. Aborting.")
        return

    original_shape = df_raw.shape
    logger.info(f"Initial products shape: {original_shape}")
    logger.info(f"Initial products columns: {list(df_raw.columns)}")

    df = df_raw.copy()

    df = standardize_formats(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = remove_outliers(df)

    save_prepared_data(df, output_file)

    logger.info(f"Original products shape:  {original_shape}")
    logger.info(f"Prepared products shape:  {df.shape}")
    logger.info("FINISHED prepare_products_data.py")
    logger.info("=====================================")


if __name__ == "__main__":
    main()
