# Pro Analytics 02 Python Starter Repository

> Use this repo to start a professional Python project.

- Additional information: <https://github.com/denisecase/pro-analytics-02>
- Project organization: [STRUCTURE](./STRUCTURE.md)
- Build professional skills:
  - **Environment Management**: Every project in isolation
  - **Code Quality**: Automated checks for fewer bugs
  - **Documentation**: Use modern project documentation tools
  # Pro Analytics 02 — Python Starter Repository

  Use this repository to start a professional Python project.

  - Additional information: <https://github.com/denisecase/pro-analytics-02>
  - Project organization: [`STRUCTURE.md`](./STRUCTURE.md)

  ## Goals

  - **Environment management:** Keep each project isolated.
  - **Code quality:** Use automated checks to reduce bugs.
  - **Documentation:** Build and serve docs with `mkdocs`.
  - **Testing:** Write and run tests with `pytest`.
  - **Version control:** Collaborate using Git and GitHub.

  ---

  ## Workflow 1 — Set Up Your Machine

  Complete the steps in [`SET_UP_MACHINE.md`](./SET_UP_MACHINE.md) and verify your environment before continuing.

  ---

  ## Workflow 2 — Set Up Your Project

  After your machine is configured, follow [`SET_UP_PROJECT.md`](./SET_UP_PROJECT.md) to create and configure this project.

  Typical commands to initialize the project environment (replace with your preferred toolchain):

  ```bash
  uv python pin 3.12
  uv venv
  uv sync --extra dev --extra docs --upgrade
  uv run pre-commit install
  uv run python --version
  ```

  Windows (PowerShell):

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

  macOS / Linux / WSL:

  ```bash
  source .venv/bin/activate
  ```

  ---

  ## Workflow 3 — Daily Workflow

  Before starting work each day:

  ### 3.1 Pull latest changes

  ```bash
  git pull
  ```

  ### 3.2 Run checks while you work

  A typical sequence for maintaining the project:

  ```bash
  uv sync --extra dev --extra docs --upgrade
  uv cache clean
  git add .
  uvx ruff check --fix
  uvx pre-commit autoupdate
  uv run pre-commit run --all-files
  git add .
  uv run pytest
  ```

  Note: the second `git add .` ensures that any automatic fixes from linters or pre-commit hooks are staged before committing.

  <details>
  <summary>Best practices note</summary>

  `uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment. For fully reproducible results, or to run a tool inside the project's `.venv`, use `uv run`.

  </details>

  ### 3.3 Build project documentation

  ```bash
  uv run mkdocs build --strict
  uv run mkdocs serve
  ```

  Open the provided local URL in your browser (Ctrl+Click on the link in the terminal). Press `Ctrl+C` to stop serving.

  ### 3.4 Execute demo modules

  Run demo modules to verify functionality:

  ```bash
  uv run python -m analytics_project.demo_module_basics
  uv run python -m analytics_project.demo_module_languages
  uv run python -m analytics_project.demo_module_stats
  uv run python -m analytics_project.demo_module_viz
  ```

  Expected results:

  - Log messages in the terminal
  - Greetings in several languages
  - Simple statistics output
  - A chart window (close to continue)

  If something fails, confirm you are in the project root and that dependencies are installed (`uv sync ...`).

  ### 3.5 Commit and push changes

  ```bash
  git add .
  git commit -m "Describe your change"
  git push -u origin main
  ```

  This triggers CI checks and may publish documentation via GitHub Pages.

  ---

  # Smart Sales — Module 2: Data Preparation

  This module adds a first step of the data pipeline: reading raw CSV files into pandas DataFrames and verifying paths and logging behavior.

  ## What I did

  - Created `src/analytics_project/data_prep.py`.
  - Added a reusable `read_and_log()` function to load CSVs with friendly logging.
  - Set up path constants using `project_root` from `utils_logger.py`.
  - Logged each file load and DataFrame shape.
  - Executed the module with `uv` and verified `project.log` is written.

  ## Raw files loaded

  Located in `data/raw/`:

  - `customers_data.csv` — 201 rows × 4 columns
  - `products_data.csv` — 100 rows × 4 columns
  - `sales_data.csv` — 2001 rows × 7 columns

  ## How to run

  Run the data preparation module:

  ```bash
  uv run python -m analytics_project.data_prep
  ```

  This prints:

  - “Starting data preparation…”
  - Messages about reading each file
  - DataFrame shapes
  - “Data preparation complete.”

  A detailed log is written to `project.log`.

  ## Git commands used

  ```bash
  git add .
  git commit -m "Implement data_prep and update project log"
  git push
  ```

  ## Result

  - Loads all raw data automatically
  - Logs all steps clearly
  - Runs with `uv` and the configured environment
  - Changes are committed and pushed to GitHub


# Smart Sales — Module 3: Data Cleaning & Reusable ETL Prep

This module extends the pipeline by cleaning and preparing all three raw datasets so they are ready for ETL into a central data store.

## What I added in this module

### Reusable `DataScrubber` class
I implemented a reusable cleaning utility located at:
src/analytics_project/data_scrubber.py


This class centralizes the core cleaning logic:

- Removing duplicate rows
- Handling missing values (drop or fill)
- Filtering numeric outliers using bounds
- Formatting string columns (lower/upper + trim)
- Renaming and reordering columns
- Parsing dates using:

pd.to_datetime(..., errors="coerce", infer_datetime_format=True)


- Inspecting the DataFrame before/after cleaning

### Dedicated prep scripts for each dataset
Inside:
src/analytics_project/data_prep/


I created three separate scripts:

- prepare_customers_data.py
- prepare_products_data.py
- prepare_sales_data.py

Each script:

1. Loads raw CSV files
2. Applies cleaning steps + DataScrubber methods
3. Saves the cleaned output into:
data/prepared/


### Validating the cleaning logic
I added a unittest file:
src/analytics_project/test_data_scrubber.py


Executed with:
uv run python src/analytics_project/test_data_scrubber.py


Output:
Ran 7 tests in 0.03s
OK


### Prepared output files
Cleaned datasets saved in:
data/prepared/



Final shapes:

- customers_data_prepared.csv — 197 rows
- products_data_prepared.csv — 96 rows
- sales_data_prepared.csv — 1906 rows (with StandardDateTime column)

## How to run the cleaning scripts
uv run python src/analytics_project/data_prep/prepare_customers_data.py
uv run python src/analytics_project/data_prep/prepare_products_data.py
uv run python src/analytics_project/data_prep/prepare_sales_data.py



## Git commands used in Module 3
git add .
git commit -m "Finished P3: DataScrubber updated, prep scripts working, cleaned customers/products/sales"
git push



## Result

- All datasets cleaned and standardized
- Centralized reusable cleaning logic
- Prep scripts fully operational
- Ready for ETL loading in the next module



# Smart Sales — Module 4: Data Warehouse (P4)

In this part of the project, I designed and implemented a small data warehouse using a classic star-schema
structure. The goal was to take the cleaned data from P3 and load it into a dimensional model that supports
fast analytical queries.

---

## ⭐ Design Choices

I followed a **star schema** with:

- **dim_customer**
- **dim_product**
- **fact_sales**

This layout keeps the model simple, consistent, and optimized for analysis.
The fact table stores grain-level transactions, while customer and product attributes live in their own
dimension tables.

### Why this schema
- Easy to query for analytics (e.g., totals by region, totals by product category)
- Natural match for the structure of the prepared CSVs
- Clean separation between facts and descriptive attributes
- Works well with SQLite and the course requirements

---

## 🏗 Schema Implementation

The ETL script located at:
src/analytics_project/dw/etl_to_dw.py


performs these steps:

1. Creates the warehouse directory and regenerates the database each run.
2. Builds the schema with the correct primary and foreign keys.
3. Reads the prepared CSV files from `data/prepared/`.
4. Normalizes and renames columns to match the DW schema.
5. Removes duplicate `customer_id` rows to avoid PK violations.
6. Loads all three tables using `pandas.to_sql()`.

### DW Schema (SQL)

CREATE TABLE IF NOT EXISTS dim_customer (
customer_id INTEGER PRIMARY KEY,
name TEXT,
region TEXT,
join_date TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
product_id INTEGER PRIMARY KEY,
product_name TEXT,
category TEXT,
unit_price REAL
);

CREATE TABLE IF NOT EXISTS fact_sales (
sale_id INTEGER PRIMARY KEY,
customer_id INTEGER,
product_id INTEGER,
sale_amount REAL,
sale_date TEXT,
FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);



---

## 📦 Result: Populated Data Warehouse

After running the ETL, the SQLite database (`data/warehouse/smart_sales_dw.db`) was populated successfully.

### dim_customer
*(Screenshot included in repo)*

### dim_product
*(Screenshot included in repo)*

### fact_sales
*(Screenshot included in repo)*

---

## 🧠 Challenges & Notes

- **Duplicate primary keys:**
  Two `customer_id` values were duplicated in the prepared CSV.
  I added logic to detect and drop duplicates automatically and log a warning.

- **Inconsistent column naming:**
  Some columns were lowercase/uppercase mixes.
  I cleaned all columns using `.str.strip().str.lower()` before renaming.

- **Schema alignment:**
  Ensuring the fact table referenced dimension tables correctly required precise
  renaming and column subset selection.

Overall, this module felt very close to what real ETL + DW work looks like — designing,
cleaning, integrating, and validating the pipeline end-to-end.

---

## 🧪 How to Run

From the project root:
uv run python -m analytics_project.dw.etl_to_dw


The script rebuilds the DW and loads all data automatically.

---

## ✔ Git Commit History
git add .
git commit -m "Add data warehouse (P4) + ETL script + populated DW screenshots"
git push

The full DW is now versioned in GitHub.

