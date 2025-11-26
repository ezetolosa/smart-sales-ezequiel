"""
analytics_project/data_prep/prepare_customers_data.py

Clean customers_data.csv and write customers_data_prepared.csv using DataScrubber.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from analytics_project.utils_logger import logger, project_root
from analytics_project.data_scrubber import DataScrubber

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
    """Read raw customers CSV."""
    file_path = RAW_DATA_DIR / file_name
    logger.info(f"READING raw customers from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded customers raw shape={df.shape}")
        return df
    except Exception as exc:
        logger.error(f"Error reading customers file {file_path}: {exc}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    """Write cleaned customers CSV."""
    file_path = PREPARED_DATA_DIR / file_name
    logger.info(f"WRITING prepared customers to: {file_path} shape={df.shape}")
    df.to_csv(file_path, index=False)


# -------------------------------------------------
# Main
# -------------------------------------------------
def main() -> None:
    logger.info("=====================================")
    logger.info("STARTING prepare_customers_data.py")
    logger.info("=====================================")

    input_file = "customers_data.csv"
    output_file = "customers_data_prepared.csv"

    df_raw = read_raw_data(input_file)
    if df_raw.empty:
        logger.error("No customers data loaded. Aborting.")
        return

    original_shape = df_raw.shape
    logger.info(f"Initial customers shape: {original_shape}")
    logger.info(f"Initial customers columns: {list(df_raw.columns)}")

    # Strip column names
    df_raw.columns = df_raw.columns.str.strip()

    # Wrap in DataScrubber
    scrubber = DataScrubber(df_raw)

    # Pipeline using DataScrubber
    scrubber.remove_duplicate_records()
    scrubber.handle_missing_data(drop=False, fill_value="Unknown")
    scrubber.format_column_strings_to_lower_and_trim(
        "CustomerName"
    ) if "CustomerName" in scrubber.df.columns else None

    # If you added numeric columns in D3.1 (e.g. "loyalty_points")
    for col in scrubber.df.select_dtypes(include="number").columns:
        scrubber.filter_column_outliers(
            col, scrubber.df[col].quantile(0.01), scrubber.df[col].quantile(0.99)
        )

    df_clean = scrubber.df
    save_prepared_data(df_clean, output_file)

    logger.info(f"Prepared customers shape:  {df_clean.shape}")
    logger.info("FINISHED prepare_customers_data.py")
    logger.info("=====================================")


if __name__ == "__main__":
    main()
