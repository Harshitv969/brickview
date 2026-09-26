"""
BrickView - Real Estate Analytics Platform
Home page (entry point). Run with: streamlit run Home.py
"""
import streamlit as st
from db import load_listing_full
from filters import render_filters

st.set_page_config(page_title="BrickView | Home", layout="wide", page_icon="🏠")

st.sidebar.title("🏠 BrickView")
filtered = render_filters()
all_listings = load_listing_full()

st.title("🏠 Real Estate Listings Dashboard")
st.caption(f"Showing {len(filtered):,} of {len(all_listings):,} listings based on current filters")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(filtered):,}")
c2.metric("Avg Price", f"${filtered['Price'].mean():,.0f}" if len(filtered) else "-")
c3.metric("Avg Price/sqft", f"${filtered['Price_per_sqft'].mean():,.0f}" if len(filtered) else "-")
c4.metric("Cities Covered", filtered["City"].nunique())

st.markdown("### Listings Table")
st.dataframe(
    filtered[["Listing_ID", "City", "Property_Type", "Price", "Area_sqft",
              "Bedrooms", "Bathrooms", "Furnishing_Status", "Agent_Name", "Listed_Date"]]
    .sort_values("Listed_Date", ascending=False),
    use_container_width=True, height=450,
)

st.markdown("---")
st.markdown(
    "Use the sidebar to jump to **Analytics**, the interactive **Map**, "
    "**SQL Queries**, **CRUD Operations**, or **About**. Filters set here "
    "carry over to Analytics and Map."
)
