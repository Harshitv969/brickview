"""
BrickView - Synthetic Data Generator
Generates the 5 raw datasets described in the project brief:
  1. listings_final_expanded.json
  2. property_attributes_final_expanded.json
  3. agents_cleaned.json
  4. sales_cleaned.csv
  5. buyers_cleaned.json

Intentionally injects some messiness (nulls, inconsistent formats) so the
cleaning step in data_prep.py has real work to do, mirroring a real capstone.
"""
import json
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

CITIES = ["New York", "San Francisco", "Los Angeles", "Chicago", "Austin",
          "Seattle", "Boston", "Denver", "Miami", "Atlanta"]
PROPERTY_TYPES = ["Apartment", "Villa", "Condo", "Townhouse", "Farmhouse"]
FURNISHING = ["Furnished", "Semi-Furnished", "Unfurnished", None]  # None = messy/missing
PAYMENT_MODES = ["Cash", "UPI", "Bank Transfer", "Cheque"]
BUYER_TYPES = ["Investor", "End User"]
BANKS = ["HDFC Bank", "Chase", "Wells Fargo", "Bank of America", "Citibank", None]

N_LISTINGS = 3000
N_AGENTS = 60

# ---------------------------------------------------------------- AGENTS ---
agents = []
for i in range(1, N_AGENTS + 1):
    deals_closed = random.randint(5, 120)
    agents.append({
        "Agent_ID": f"AG{i:03d}",
        "Name": fake.name(),
        "City": random.choice(CITIES),
        "Contact": fake.email() if random.random() > 0.5 else fake.phone_number(),
        "Commission_Rate": round(random.uniform(1.0, 6.0), 2),
        "Deals_Closed": deals_closed,
        "Rating": round(random.uniform(2.5, 5.0), 1) if random.random() > 0.05 else None,
        "Experience_Years": random.randint(1, 25),
        "Avg_Closing_Days": random.randint(15, 90),
    })

with open("data/agents_cleaned.json", "w") as f:
    json.dump(agents, f, indent=2)

# -------------------------------------------------------------- LISTINGS ---
listings = []
listing_ids = []
base_date = datetime(2023, 1, 1)

CITY_COORDS = {
    "New York": (40.7128, -74.0060), "San Francisco": (37.7749, -122.4194),
    "Los Angeles": (34.0522, -118.2437), "Chicago": (41.8781, -87.6298),
    "Austin": (30.2672, -97.7431), "Seattle": (47.6062, -122.3321),
    "Boston": (42.3601, -71.0589), "Denver": (39.7392, -104.9903),
    "Miami": (25.7617, -80.1918), "Atlanta": (33.7490, -84.3880),
}

for i in range(1, N_LISTINGS + 1):
    lid = f"L{i:04d}"
    listing_ids.append(lid)
    city = random.choice(CITIES)
    lat, lon = CITY_COORDS[city]
    ptype = random.choice(PROPERTY_TYPES)
    area = random.randint(450, 4500)
    price_per_sqft = random.uniform(150, 900)
    price = round(area * price_per_sqft, -2)
    listed_date = base_date + timedelta(days=random.randint(0, 900))
    # inject a few messy date string formats
    if random.random() < 0.1:
        date_str = listed_date.strftime("%d-%m-%Y")
    else:
        date_str = listed_date.strftime("%Y-%m-%d")

    listings.append({
        "Listing_ID": lid,
        "City": city,
        "Property_Type": ptype,
        "Price": price if random.random() > 0.02 else None,  # occasional missing price
        "Area_sqft": area,
        "Agent_ID": random.choice(agents)["Agent_ID"],
        "Listed_Date": date_str,
        "Latitude": round(lat + random.uniform(-0.05, 0.05), 6),
        "Longitude": round(lon + random.uniform(-0.05, 0.05), 6),
    })

with open("data/listings_final_expanded.json", "w") as f:
    json.dump(listings, f, indent=2)

# ------------------------------------------------------- PROPERTY ATTRS ---
attrs = []
for i, lid in enumerate(listing_ids, start=1):
    is_rented = random.choice([True, False, None]) if random.random() < 0.05 else random.choice([True, False])
    attrs.append({
        "Attribute_ID": f"AT{i:04d}",
        "Listing_ID": lid,
        "Bedrooms": random.randint(1, 6),
        "Bathrooms": random.randint(1, 5),
        "Floor_Number": random.randint(0, 30),
        "Total_Floors": random.randint(1, 35),
        "Year_Built": random.randint(1975, 2024),
        "Is_Rented": is_rented,
        "Tenant_Count": random.randint(0, 5) if is_rented else 0,
        "Furnishing_Status": random.choice(FURNISHING),
        "Metro_Distance_Km": round(random.uniform(0.1, 15.0), 2),
        "Parking_Available": random.choice([True, False]),
        "Power_Backup": random.choice([True, False]),
    })

with open("data/property_attributes_final_expanded.json", "w") as f:
    json.dump(attrs, f, indent=2)

# ------------------------------------------------------------------ SALES ---
# Not every listing sells
sold_listings = random.sample(listing_ids, k=int(N_LISTINGS * 0.65))
sales_rows = []
for i, lid in enumerate(sold_listings, start=1):
    listing = next(l for l in listings if l["Listing_ID"] == lid)
    list_price = listing["Price"] or 300000
    listed_dt = base_date + timedelta(days=random.randint(0, 900))
    days_on_market = random.randint(5, 180)
    sale_dt = listed_dt + timedelta(days=days_on_market)
    price_mult = random.uniform(0.90, 1.12)
    sale_price = round(list_price * price_mult, -2)
    sales_rows.append({
        "Sale_ID": f"S{i:04d}",
        "Listing_ID": lid,
        "Sale_Date": sale_dt.strftime("%Y-%m-%d"),
        "Sale_Price": sale_price,
        "Days_On_Market": days_on_market,
    })

with open("data/sales_cleaned.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Sale_ID", "Listing_ID", "Sale_Date", "Sale_Price", "Days_On_Market"])
    writer.writeheader()
    writer.writerows(sales_rows)

# ----------------------------------------------------------------- BUYERS ---
buyers = []
for i, sale in enumerate(sales_rows, start=1):
    loan_taken = random.choice([True, False])
    buyers.append({
        "Buyer_ID": f"B{i:04d}",
        "Sale_ID": sale["Sale_ID"],
        "Buyer_Type": random.choice(BUYER_TYPES),
        "Payment_Mode": random.choice(PAYMENT_MODES),
        "Loan_Taken": loan_taken,
        "Loan_Provider": random.choice(BANKS) if loan_taken else None,
        "Loan_Amount": round(sale["Sale_Price"] * random.uniform(0.5, 0.85), -2) if loan_taken else 0,
    })

with open("data/buyers_cleaned.json", "w") as f:
    json.dump(buyers, f, indent=2)

print(f"Generated: {len(agents)} agents, {len(listings)} listings, "
      f"{len(attrs)} attribute rows, {len(sales_rows)} sales, {len(buyers)} buyers")
