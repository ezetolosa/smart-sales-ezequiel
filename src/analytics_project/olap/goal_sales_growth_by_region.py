"""
Goal Script: Sales Growth by Region
Author: Eze Tolosa

This script takes the cube created in P6 (sales_growth_by_region_cube.csv),
normalizes region names, computes total revenue by region, and identifies
which regions perform best.

It serves as the final analysis deliverable for Module 6 (OLAP).
"""

import pathlib
import pandas as pd
import matplotlib.pyplot as plt

from analytics_project.utils_logger import logger

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

THIS_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CUBE_DIR = DATA_DIR / "olap_cubing_outputs"
RESULTS_DIR = DATA_DIR / "results"

CUBE_FILE = CUBE_DIR / "sales_growth_by_region_cube.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Region Normalization Mapping
# -------------------------------------------------------------------

REGION_MAP = {
    "east": "EAST",
    "eas": "EAST",
    "west": "WEST",
    "south-west": "SOUTH-WEST",
    "southwest": "SOUTH-WEST",
    "south": "SOUTH",
    "north": "NORTH",
    "central": "CENTRAL",
}


def normalize_region(region: str) -> str:
    """Clean and standardize region names."""
    if not isinstance(region, str):
        return "UNKNOWN"

    cleaned = region.strip().lower().replace("_", "-")

    return REGION_MAP.get(cleaned, cleaned.upper())


# -------------------------------------------------------------------
# Analysis Logic
# -------------------------------------------------------------------


def load_cube():
    """Load the previously created cube into a dataframe."""
    logger.info(f"Loading cube from: {CUBE_FILE}")
    return pd.read_csv(CUBE_FILE)


def clean_cube(df: pd.DataFrame) -> pd.DataFrame:
    """Apply region normalization and return a clean cube."""
    logger.info("Normalizing region names...")

    df["region_clean"] = df["region"].apply(normalize_region)

    # Group duplicate cleaned regions
    df_clean = (
        df.groupby(["Year", "Month", "region_clean"])
        .agg({"TotalRevenue": "sum", "TransactionCount": "sum"})
        .reset_index()
    )

    logger.info("Cube cleaned and normalized.")
    return df_clean


def summarize(df: pd.DataFrame):
    """Compute total revenue by region."""
    summary = (
        df.groupby("region_clean")["TotalRevenue"].sum().sort_values(ascending=False).reset_index()
    )
    return summary


def plot_summary(summary_df: pd.DataFrame):
    """Create a bar chart of revenue by region."""
    plt.figure(figsize=(10, 6))
    plt.bar(summary_df["region_clean"], summary_df["TotalRevenue"])
    plt.title("Total Revenue by Region")
    plt.xlabel("Region")
    plt.ylabel("Revenue")
    plt.tight_layout()

    output_path = RESULTS_DIR / "sales_growth_by_region.png"
    plt.savefig(output_path)
    plt.close()

    logger.info(f"Plot saved to: {output_path}")


def main():
    logger.info("Starting Goal: Sales Growth by Region")

    # Load cube
    cube = load_cube()

    # Clean + normalize regions
    cube_clean = clean_cube(cube)

    # Summaries
    summary = summarize(cube_clean)
    print("\n=== Revenue by Region ===")
    print(summary)

    # Save summary
    summary_path = RESULTS_DIR / "sales_growth_by_region_summary.csv"
    summary.to_csv(summary_path, index=False)
    logger.info(f"Summary saved to: {summary_path}")

    # Visualization
    plot_summary(summary)

    logger.info("Goal analysis completed successfully.")


if __name__ == "__main__":
    main()
