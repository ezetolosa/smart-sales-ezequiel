"""
analytics_project/data_prep/prepare_products_data.py

Clean products_data.csv and write products_data_prepared.csv using DataScrubber.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from analytics_project.utils_logger import logger, project_root
from analytics_project.data_scrubber import DataScrubber

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
    except Exception as exc:
        logger.error(f"Error reading products file {file_path}: {exc}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    file_path = PREPARED_DATA_DIR / file_name
    logger.info(f"WRITING prepared products to: {file_path} shape={df.shape}")
    df.to_csv(file_path, index=False)


def main() -> None:
    logger.info("=====================================")
    logger.info("STARTING prepare_products_data.py")
    logger.info("=====================================")

    input_file = "products_data.csv"
    output_file = "products_data_prepared.csv"

    df_raw = read_raw_data(input_file)
    if df_raw.empty:
        logger.error("No products data loaded. Aborting.")
        return

    original_shape = df_raw.shape
    logger.info(f"Initial products shape: {original_shape}")
    logger.info(f"Initial products columns: {list(df_raw.columns)}")

    scrubber = DataScrubber(df_raw.copy())

    # Standardize column names
    scrubber.df.columns = scrubber.df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Pipeline
    scrubber.remove_duplicate_records()
    scrubber.handle_missing_data(fill_value="Unknown")

    # Format relevant string columns
    string_cols = scrubber.df.select_dtypes(include="object").columns
    for col in string_cols:
        scrubber.format_column_strings_to_lower_and_trim(col)

    # Outliers for numeric columns
    numeric_cols = scrubber.df.select_dtypes(include="number").columns
    for col in numeric_cols:
        q_low = scrubber.df[col].quantile(0.01)
        q_high = scrubber.df[col].quantile(0.99)
        scrubber.filter_column_outliers(col, q_low, q_high)

    df_clean = scrubber.df
    save_prepared_data(df_clean, output_file)

    logger.info(f"Prepared products shape:  {df_clean.shape}")
    logger.info("FINISHED prepare_products_data.py")
    logger.info("=====================================")


if __name__ == "__main__":
    main()
