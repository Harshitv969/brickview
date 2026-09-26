"""BrickView - About page: schema and project overview."""
import streamlit as st
from db import run_query

st.set_page_config(page_title="BrickView | About", layout="wide", page_icon="ℹ️")
st.sidebar.title("🏠 BrickView")
st.title("ℹ️ About BrickView")

st.markdown("""
**BrickView** is an end-to-end real estate analytics platform: raw JSON/CSV
data → cleaned & normalized SQLite database → 30 business SQL queries →
interactive Streamlit dashboard with filters, visualizations, an interactive
clustered map, and full CRUD.
""")

st.markdown("### Database Schema")
st.code("""
agents (Agent_ID PK)
listings (Listing_ID PK, Agent_ID FK -> agents)
property_attributes (Attribute_ID PK, Listing_ID FK -> listings)
sales (Sale_ID PK, Listing_ID FK -> listings)
buyers (Buyer_ID PK, Sale_ID FK -> sales)

Views: v_listing_full, v_sales_full
""", language="text")

st.markdown("### Table Row Counts")
counts = {}
for t in ["agents", "listings", "property_attributes", "sales", "buyers"]:
    counts[t] = run_query(f"SELECT COUNT(*) AS n FROM {t}").iloc[0]["n"]
st.table(counts)

st.markdown("### Tech Stack")
st.markdown("- **Python / Pandas** — data cleaning\n"
            "- **SQLite** — normalized relational database\n"
            "- **Streamlit** — multi-page dashboard\n"
            "- **Plotly** — bar/pie/line charts\n"
            "- **Folium + streamlit-folium** — interactive clustered map")
