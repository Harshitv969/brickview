# BrickView – Real Estate Analytics Platform

An end-to-end real estate analytics project: synthetic data → **EDA** →
normalized **SQL** database (with foreign-key enforcement) → 30 business SQL
queries → a multi-page **Streamlit** dashboard with global filters, charts, an
interactive clustered map, and full type-safe CRUD.

## Project Structure

```
brickview/
├── data/
│   ├── listings_final_expanded.json
│   ├── property_attributes_final_expanded.json
│   ├── agents_cleaned.json
│   ├── sales_cleaned.csv
│   └── buyers_cleaned.json
├── eda/
│   └── EDA.ipynb           # exploratory data analysis on the raw datasets
├── sql/
│   ├── schema.sql          # plain-SQL version of the normalized schema
│   └── queries.sql         # all 30 business queries as a runnable .sql file
├── generate_data.py       # creates the 5 raw datasets (synthetic, seeded, ~3000 listings)
├── build_database.py      # cleans data + builds brickview.db (SQLite, FKs ON)
├── sql_queries.py         # same 30 queries, as a Python dict feeding the Streamlit UI
├── db.py                  # shared DB connection helper (FK pragma, cached loaders)
├── filters.py             # shared sidebar filters (persist across pages via session_state)
├── Home.py                # entry point — run this with `streamlit run`
├── pages/
│   ├── 1_Analytics.py     # bar / pie / line charts
│   ├── 2_Map.py           # Folium map with marker clustering
│   ├── 3_SQL_Queries.py   # all 30 queries as expandable cards + live results
│   ├── 4_CRUD.py          # type-safe CRUD with FK validation, for all 5 tables
│   └── 5_About.py         # schema + tech stack overview
├── brickview.db           # the built SQLite database (already generated)
├── requirements.txt
└── README.md
```

## Exploratory Data Analysis

[`eda/EDA.ipynb`](eda/EDA.ipynb) checks the raw datasets before cleaning —
shape and dtypes for each of the 5 sources, missing-value counts, price
distribution, price by city/property type, area-vs-price and metro-distance-
vs-price correlations, days-on-market distribution, and buyer/payment-mode
splits — with a **Key Takeaways** section at the end calling out real findings
(e.g. `Furnishing_Status` is missing for ~27% of listings, and 156 buyers who
took a loan have no `Loan_Provider` recorded, which the current cleaning
pipeline doesn't yet handle). This is what motivated the shape of the 30 SQL
queries below.

To re-run it: `pip install -r requirements-eda.txt` (adds matplotlib/seaborn/
jupyter on top of the app's own dependencies), then `jupyter notebook eda/EDA.ipynb`.

Streamlit auto-detects the `pages/` folder and turns it into the sidebar
navigation — `Home.py` is the entry point (`streamlit run Home.py`).

## Setup

```bash
pip install -r requirements.txt
```

## (Optional) Regenerate data and database from scratch

The repo ships with `brickview.db` already built, so this is optional. Run it
if you want fresh synthetic data or to plug in real datasets:

```bash
python generate_data.py     # writes data/*.json and data/*.csv (~3,000 listings)
python build_database.py    # rebuilds brickview.db from the data/ files
```

If your instructor gives you the *actual* datasets, drop them into `data/`
with the same filenames and just re-run `build_database.py` — everything
downstream (queries, app) works unchanged since it's built against the
schema, not the synthetic values.

## Run the dashboard

```bash
streamlit run Home.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Pages

1. **Home** – KPI summary + filtered listings table.
2. **Analytics** – avg price by city, property type distribution, listings by
   city, monthly sales trend, furnishing vs. price.
3. **Map** – interactive Folium map with marker clustering and popups
   (listing ID, price, agent) — a real upgrade over a flat point map, and
   handles thousands of listings without becoming unreadable.
4. **SQL Queries** – all 30 business questions from the brief, grouped into
   Property & Pricing, Sales & Market Performance, Agent Performance, and
   Buyer & Financing Behavior, each with the raw SQL and a live result table.
   The same queries also live in [`sql/queries.sql`](sql/queries.sql) as a
   plain, runnable SQL file (`sqlite3 brickview.db < sql/queries.sql`).
5. **CRUD** – full Create / Read / Update / Delete for all 5 tables, with:
   - **proper type casting** (numbers as numbers, booleans as checkboxes,
     dates as date pickers — not raw strings),
   - **foreign key validation** before insert/update (e.g. an Agent_ID on a
     listing must actually exist in `agents`),
   - **FK enforcement at the database level** (`PRAGMA foreign_keys = ON`),
     so e.g. deleting an agent who still has active listings raises a clear
     error instead of silently orphaning rows.
6. **About** – schema diagram, row counts, tech stack.

Filters set on any page (City, Property Type, Price Range, Agent, Listed Date
Range) persist across Home / Analytics / Map via `st.session_state`.

## Database Schema

```
agents (Agent_ID PK)
listings (Listing_ID PK, Agent_ID FK -> agents)
property_attributes (Attribute_ID PK, Listing_ID FK -> listings)
sales (Sale_ID PK, Listing_ID FK -> listings)
buyers (Buyer_ID PK, Sale_ID FK -> sales)

Views: v_listing_full, v_sales_full
```

Indexes on all join columns (City, Agent_ID, Listing_ID, Sale_ID). The same
`CREATE TABLE`/`CREATE VIEW` statements are also in
[`sql/schema.sql`](sql/schema.sql) as a plain SQL file.

## Why SQLite instead of MySQL

The brief allows either ("SQL (MySQL/SQLite)"). SQLite was used here because
it needs no separate server process — `brickview.db` is a single file that
ships with the repo and works immediately on any machine, which is one less
moving part for a capstone demo. The schema, queries, and joins are
standard SQL and would port to MySQL with only minor syntax changes (e.g.
`AUTO_INCREMENT` vs `INTEGER PRIMARY KEY`, `STR_TO_DATE`/`DATE_FORMAT`
instead of `strftime`). Ask if you'd like a MySQL version instead.

## Deploying to Streamlit Community Cloud

1. Push this folder to a GitHub repo (include `brickview.db`).
2. Go to https://share.streamlit.io, connect the repo, and point it at `Home.py`.
3. Streamlit Cloud installs `requirements.txt` automatically.
