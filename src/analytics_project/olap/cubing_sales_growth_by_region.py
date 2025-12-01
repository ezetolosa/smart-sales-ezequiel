"""
OLAP Cubing Script – Sales Growth by Region (P6).

Este script crea un cubo con revenue mensual por región
a partir del DW (smart_sales_dw.db).
"""

import pathlib
import sqlite3

import pandas as pd

from analytics_project.utils_logger import logger

# ==== Paths ====
THIS_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
PACKAGE_DIR: pathlib.Path = THIS_DIR.parent
SRC_DIR: pathlib.Path = PACKAGE_DIR.parent
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent

DATA_DIR: pathlib.Path = PROJECT_ROOT_DIR / "data"
WAREHOUSE_DIR: pathlib.Path = DATA_DIR / "warehouse"

# 👇 IMPORTANTE: mismo nombre que en etl_to_dw.py
DB_PATH: pathlib.Path = WAREHOUSE_DIR / "smart_sales_dw.db"

OLAP_OUTPUT_DIR: pathlib.Path = DATA_DIR / "olap_cubing_outputs"
OLAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ingest_sales_with_region_from_dw() -> pd.DataFrame:
    """
    Leer ventas + región desde el DW.

    Usa fact_sales + dim_customer, que son las tablas de tu esquema.
    """

    query = """
        SELECT
            s.sale_id,
            s.customer_id,
            s.product_id,
            s.sale_date,
            s.sale_amount,
            c.region
        FROM fact_sales AS s
        JOIN dim_customer AS c
            ON s.customer_id = c.customer_id
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info("Sales + region loaded from DW (fact_sales + dim_customer).")
        return df
    except Exception as e:
        logger.error(f"Error loading data from DW: {e}")
        raise


def create_sales_growth_cube(df: pd.DataFrame) -> pd.DataFrame:
    """Crear cubo mensual por región."""

    # 1) Asegurar que sale_date sea fecha válida
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    invalid_dates = df["sale_date"].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"Dropping {invalid_dates} rows with invalid sale_date values.")
        df = df.dropna(subset=["sale_date"])

    # 2) Asegurar que sale_amount sea numérico
    df["sale_amount"] = (
        df["sale_amount"]
        .astype(str)  # todo a string
        .str.strip()  # saco espacios
        .replace(["", "NA", "N/A", "null", "None"], pd.NA)
    )
    df["sale_amount"] = pd.to_numeric(df["sale_amount"], errors="coerce")

    invalid_amounts = df["sale_amount"].isna().sum()
    if invalid_amounts > 0:
        logger.warning(f"Dropping {invalid_amounts} rows with invalid sale_amount values.")
        df = df.dropna(subset=["sale_amount"])

    # 3) Crear columnas de tiempo
    df["Year"] = df["sale_date"].dt.year
    df["Month"] = df["sale_date"].dt.month

    # 4) Agrupar por Year-Month-Region
    grouped = (
        df.groupby(["Year", "Month", "region"])
        .agg(
            TotalRevenue=("sale_amount", "sum"),
            TransactionCount=("sale_id", "count"),
        )
        .reset_index()
    )

    logger.info("Sales growth cube created (Year-Month-Region).")
    return grouped


def write_cube_to_csv(cube: pd.DataFrame, filename: str) -> None:
    """Guardar el cubo en CSV."""
    output_path = OLAP_OUTPUT_DIR / filename
    cube.to_csv(output_path, index=False)
    logger.info(f"Cube saved to {output_path}")


def main():
    logger.info("Starting cubing: sales growth by region...")

    df = ingest_sales_with_region_from_dw()
    if df.empty:
        logger.warning(
            "WARNING: No data returned from DW. Run ETL to DW before running this cubing script."
        )

    cube = create_sales_growth_cube(df)
    write_cube_to_csv(cube, "sales_growth_by_region_cube.csv")

    logger.info("Cubing completed successfully.")


if __name__ == "__main__":
    main()
