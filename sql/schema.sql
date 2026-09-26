-- BrickView - Database Schema
-- Normalized SQLite schema: 5 tables, foreign keys, indexes on join
-- columns, and two convenience views used by the Streamlit app.
-- (Mirrors the schema created programmatically in build_database.py.)

PRAGMA foreign_keys = ON;

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

-- Denormalized view joining a listing with its attributes and agent,
-- used by the Streamlit app's Home/Analytics/Map pages.
CREATE VIEW v_listing_full AS
SELECT l.Listing_ID, l.City, l.Property_Type, l.Price, l.Area_sqft,
       l.Price_per_sqft, l.Listed_Date, l.Latitude, l.Longitude,
       a.Bedrooms, a.Bathrooms, a.Furnishing_Status, a.Metro_Distance_Km,
       a.Is_Rented, a.Parking_Available, a.Power_Backup, a.Year_Built,
       ag.Name AS Agent_Name, ag.Rating AS Agent_Rating
FROM listings l
LEFT JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
LEFT JOIN agents ag ON l.Agent_ID = ag.Agent_ID;

-- Denormalized view joining a sale back to its listing, with the
-- sale-to-list price ratio precomputed.
CREATE VIEW v_sales_full AS
SELECT s.Sale_ID, s.Listing_ID, s.Sale_Date, s.Sale_Price, s.Days_On_Market,
       l.Price AS List_Price, l.City, l.Property_Type, l.Agent_ID,
       ROUND(s.Sale_Price * 1.0 / l.Price, 3) AS Sale_To_List_Ratio
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID;
