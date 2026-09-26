"""
BrickView - Data Preparation & Database Builder
Reads the 5 raw datasets, cleans them, and loads them into a normalized
SQLite database (brickview.db) with PKs, FKs, indexes, and a couple of
useful views.
"""
import json
import sqlite3
import pandas as pd
import os

DB_PATH = "brickview.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# ---------------------------------------------------------- 1. LOAD RAW ---
with open("data/listings_final_expanded.json") as f:
    listings = pd.DataFrame(json.load(f))

with open("data/property_attributes_final_expanded.json") as f:
    attrs = pd.DataFrame(json.load(f))

with open("data/agents_cleaned.json") as f:
    agents = pd.DataFrame(json.load(f))

sales = pd.read_csv("data/sales_cleaned.csv")

with open("data/buyers_cleaned.json") as f:
    buyers = pd.DataFrame(json.load(f))

# --------------------------------------------------------- 2. CLEAN DATA ---
# Listings: standardize dates, fill missing prices with city-type median
listings["Listed_Date"] = pd.to_datetime(listings["Listed_Date"], format="mixed", dayfirst=False)
listings["Price"] = listings.groupby(["City", "Property_Type"])["Price"] \
    .transform(lambda s: s.fillna(s.median()))
listings["Price"] = listings["Price"].fillna(listings["Price"].median())
listings["Price_per_sqft"] = (listings["Price"] / listings["Area_sqft"]).round(2)

# Property attributes: normalize booleans, fill missing furnishing/rented
attrs["Is_Rented"] = attrs["Is_Rented"].fillna(False).astype(bool)
attrs["Furnishing_Status"] = attrs["Furnishing_Status"].fillna("Unfurnished")
attrs["Parking_Available"] = attrs["Parking_Available"].astype(bool)
attrs["Power_Backup"] = attrs["Power_Backup"].astype(bool)

# Agents: fill missing ratings with overall average
agents["Rating"] = agents["Rating"].fillna(round(agents["Rating"].mean(), 1))

# Sales: standardize date
sales["Sale_Date"] = pd.to_datetime(sales["Sale_Date"])

# Buyers: normalize booleans
buyers["Loan_Taken"] = buyers["Loan_Taken"].astype(bool)

# ------------------------------------------------------- 3. LOAD TO SQL ---
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()
cur.executescript("""
CREATE TABLE agents (
    Agent_ID TEXT PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Contact TEXT,
    Commission_Rate REAL,
    Deals_Closed INTEGER,
    Rating REAL,
    Experience_Years INTEGER,
    Avg_Closing_Days INTEGER
);

CREATE TABLE listings (
    Listing_ID TEXT PRIMARY KEY,
    City TEXT,
    Property_Type TEXT,
    Price REAL,
    Area_sqft INTEGER,
    Price_per_sqft REAL,
    Agent_ID TEXT,
    Listed_Date TEXT,
    Latitude REAL,
    Longitude REAL,
    FOREIGN KEY (Agent_ID) REFERENCES agents(Agent_ID)
);

CREATE TABLE property_attributes (
    Attribute_ID TEXT PRIMARY KEY,
    Listing_ID TEXT,
    Bedrooms INTEGER,
    Bathrooms INTEGER,
    Floor_Number INTEGER,
    Total_Floors INTEGER,
    Year_Built INTEGER,
    Is_Rented INTEGER,
    Tenant_Count INTEGER,
    Furnishing_Status TEXT,
    Metro_Distance_Km REAL,
    Parking_Available INTEGER,
    Power_Backup INTEGER,
    FOREIGN KEY (Listing_ID) REFERENCES listings(Listing_ID)
);

CREATE TABLE sales (
    Sale_ID TEXT PRIMARY KEY,
    Listing_ID TEXT,
    Sale_Date TEXT,
    Sale_Price REAL,
    Days_On_Market INTEGER,
    FOREIGN KEY (Listing_ID) REFERENCES listings(Listing_ID)
);

CREATE TABLE buyers (
    Buyer_ID TEXT PRIMARY KEY,
    Sale_ID TEXT,
    Buyer_Type TEXT,
    Payment_Mode TEXT,
    Loan_Taken INTEGER,
    Loan_Provider TEXT,
    Loan_Amount REAL,
    FOREIGN KEY (Sale_ID) REFERENCES sales(Sale_ID)
);

CREATE INDEX idx_listings_city ON listings(City);
CREATE INDEX idx_listings_agent ON listings(Agent_ID);
CREATE INDEX idx_attrs_listing ON property_attributes(Listing_ID);
CREATE INDEX idx_sales_listing ON sales(Listing_ID);
CREATE INDEX idx_buyers_sale ON buyers(Sale_ID);

CREATE VIEW v_listing_full AS
SELECT l.Listing_ID, l.City, l.Property_Type, l.Price, l.Area_sqft,
       l.Price_per_sqft, l.Listed_Date, l.Latitude, l.Longitude,
       a.Bedrooms, a.Bathrooms, a.Furnishing_Status, a.Metro_Distance_Km,
       a.Is_Rented, a.Parking_Available, a.Power_Backup, a.Year_Built,
       ag.Name AS Agent_Name, ag.Rating AS Agent_Rating
FROM listings l
LEFT JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
LEFT JOIN agents ag ON l.Agent_ID = ag.Agent_ID;

CREATE VIEW v_sales_full AS
SELECT s.Sale_ID, s.Listing_ID, s.Sale_Date, s.Sale_Price, s.Days_On_Market,
       l.Price AS List_Price, l.City, l.Property_Type, l.Agent_ID,
       ROUND(s.Sale_Price * 1.0 / l.Price, 3) AS Sale_To_List_Ratio
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID;
""")
conn.commit()

agents.to_sql("agents", conn, if_exists="append", index=False)
listings.to_sql("listings", conn, if_exists="append", index=False)
attrs.to_sql("property_attributes", conn, if_exists="append", index=False)
sales.to_sql("sales", conn, if_exists="append", index=False)
buyers.to_sql("buyers", conn, if_exists="append", index=False)

conn.commit()

counts = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
          for t in ["agents", "listings", "property_attributes", "sales", "buyers"]}
print("Row counts:", counts)

conn.close()
print(f"Database built at {DB_PATH}")
