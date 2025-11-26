"""ETL script to load prepared data into the data warehouse (SQLite database).

File: src/analytics_project/dw/etl_to_dw.py

This file assumes the following structure (yours may vary):

project_root/
│
├─ data/
│   ├─ raw/
│   ├─ prepared/
│   └─ warehouse/
│
└─ src/
    └─ analytics_project/
        ├─ data_preparation/
        ├─ dw/
        ├─ analytics/
        └─ utils_logger.py

By switching to a modern src/ layout and using __init__.py files,
we no longer need any sys.path modifications.

Remember to put __init__.py files (empty is fine) in each folder to make them packages.

NOTE on column names: This example uses inconsistent naming conventions for column names in the cleaned data.
A good business intelligence project would standardize these during data preparation.
Your names should be more standard after cleaning and pre-processing the data.

Database names generally follow snake_case conventions for SQL compatibility.
"snake_case" =  all lowercase with underscores between words.
"""

# Imports at the top

import pathlib
import sqlite3
import pandas as pd

from analytics_project.utils_logger import logger

# -------------------------------------------------------------------
# PATHS
# -------------------------------------------------------------------

THIS_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
DW_DIR: pathlib.Path = THIS_DIR
PACKAGE_DIR: pathlib.Path = DW_DIR.parent
SRC_DIR: pathlib.Path = PACKAGE_DIR.parent
PROJECT_ROOT: pathlib.Path = SRC_DIR.parent

DATA_DIR: pathlib.Path = PROJECT_ROOT / "data"
PREPARED_DIR: pathlib.Path = DATA_DIR / "prepared"
WAREHOUSE_DIR: pathlib.Path = DATA_DIR / "warehouse"

DB_PATH: pathlib.Path = WAREHOUSE_DIR / "smart_sales_dw.db"

logger.info(f"THIS_DIR:         {THIS_DIR}")
logger.info(f"DATA_DIR:         {DATA_DIR}")
logger.info(f"PREPARED_DIR:     {PREPARED_DIR}")
logger.info(f"WAREHOUSE_DIR:    {WAREHOUSE_DIR}")
logger.info(f"DB_PATH:          {DB_PATH}")

# -------------------------------------------------------------------
# CREATE SCHEMA
# -------------------------------------------------------------------


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create DW tables (star schema)."""

    logger.info("Creating DW tables (dim_customer, dim_product, fact_sales).")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            join_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_sales (
            sale_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            sale_amount REAL,
            sale_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
            FOREIGN KEY (product_id)  REFERENCES dim_product(product_id)
        )
    """)

    logger.info("DW schema created successfully.")


# -------------------------------------------------------------------
# LOAD DIM CUSTOMER
# -------------------------------------------------------------------


def load_dim_customer(conn: sqlite3.Connection) -> None:
    path = PREPARED_DIR / "customers_data_prepared.csv"
    logger.info(f"Loading dim_customer from: {path}")

    df = pd.read_csv(path)
    logger.info(f"dim_customer input shape: {df.shape}")

    # Normalize + rename columns
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(
        columns={
            "customerid": "customer_id",
            "name": "name",
            "region": "region",
            "joindate": "join_date",
        }
    )

    # Keep only DW columns
    df = df[["customer_id", "name", "region", "join_date"]]

    # Drop any duplicate customer_id rows from the prepared file to avoid
    # violating the UNIQUE/PRIMARY KEY constraint when inserting into the
    # dimension table. Keep the first occurrence and log how many duplicates
    # were removed so the user can investigate data-preparation issues.
    if "customer_id" in df.columns:
        dup_mask = df.duplicated(subset=["customer_id"], keep=False)
        if dup_mask.any():
            num_dups = dup_mask.sum()
            logger.warning(
                f"Found {num_dups} duplicate row(s) for 'customer_id' in prepared file; "
                "dropping duplicates before load (keeping first occurrence)."
            )
            df = df.drop_duplicates(subset=["customer_id"], keep="first")

    df.to_sql("dim_customer", conn, if_exists="append", index=False)
    logger.info("Loaded dim_customer.")


# -------------------------------------------------------------------
# LOAD DIM PRODUCT
# -------------------------------------------------------------------


def load_dim_product(conn: sqlite3.Connection) -> None:
    path = PREPARED_DIR / "products_data_prepared.csv"
    logger.info(f"Loading dim_product from: {path}")

    df = pd.read_csv(path)
    logger.info(f"dim_product input shape: {df.shape}")

    # Normalize + rename columns
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(
        columns={
            "productid": "product_id",
            "productname": "product_name",
            "category": "category",
            "unitprice": "unit_price",
        }
    )

    # Keep only DW schema columns
    df = df[["product_id", "product_name", "category", "unit_price"]]

    df.to_sql("dim_product", conn, if_exists="append", index=False)
    logger.info("Loaded dim_product.")


# -------------------------------------------------------------------
# LOAD FACT SALES
# -------------------------------------------------------------------


def load_fact_sales(conn: sqlite3.Connection) -> None:
    path = PREPARED_DIR / "sales_data_prepared.csv"
    logger.info(f"Loading fact_sales from: {path}")

    df = pd.read_csv(path)
    logger.info(f"fact_sales input shape: {df.shape}")

    df.columns = df.columns.str.strip().str.lower()

    df = df.rename(
        columns={
            "transactionid": "sale_id",
            "customerid": "customer_id",
            "productid": "product_id",
            "saleamount": "sale_amount",
            "saledate": "sale_date",
        }
    )

    # Keep only DW schema columns
    df = df[["sale_id", "customer_id", "product_id", "sale_amount", "sale_date"]]

    df.to_sql("fact_sales", conn, if_exists="append", index=False)
    logger.info("Loaded fact_sales.")


# -------------------------------------------------------------------
# MAIN ETL PROCESS
# -------------------------------------------------------------------


def load_data_to_dw() -> None:
    logger.info("Starting ETL to Data Warehouse.")

    WAREHOUSE_DIR.mkdir(exist_ok=True)

    if DB_PATH.exists():
        logger.info(f"Deleting existing DW database at: {DB_PATH}")
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        create_schema(cursor)
        conn.commit()

        load_dim_customer(conn)
        load_dim_product(conn)
        load_fact_sales(conn)

        conn.commit()
        logger.info("ETL completed successfully.")

    finally:
        logger.info("Closing DW connection.")
        conn.close()


# -------------------------------------------------------------------

if __name__ == "__main__":
    load_data_to_dw()
