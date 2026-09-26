"""BrickView - Analytics page: bar/pie/line charts."""
import streamlit as st
import plotly.express as px
import pandas as pd

from db import load_sales_full
from filters import render_filters

st.set_page_config(page_title="BrickView | Analytics", layout="wide", page_icon="📊")

st.sidebar.title("🏠 BrickView")
filtered = render_filters()

st.title("📊 Analytics")

if len(filtered) == 0:
    st.warning("No data matches the current filters — adjust filters in the sidebar.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Price by City")
    by_city = filtered.groupby("City", as_index=False)["Price"].mean().sort_values("Price", ascending=False)
    fig = px.bar(by_city, x="City", y="Price", color="City")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribution of Property Types")
    by_type = filtered["Property_Type"].value_counts().reset_index()
    by_type.columns = ["Property_Type", "Count"]
    fig = px.pie(by_type, names="Property_Type", values="Count")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Listings Count by City")
    counts = filtered["City"].value_counts().reset_index()
    counts.columns = ["City", "Count"]
    fig = px.bar(counts, x="City", y="Count", color="City")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Monthly Sales Trend")
    sales_df = load_sales_full().copy()
    # Filter sales by the listings that match active sidebar filters
    sales_df = sales_df[sales_df["Listing_ID"].isin(filtered["Listing_ID"])]
    sales_df["Month"] = sales_df["Sale_Date"].dt.to_period("M").astype(str)
    monthly = sales_df.groupby("Month", as_index=False) \
        .agg(Sales_Count=("Sale_ID", "count"), Revenue=("Sale_Price", "sum"))
    fig = px.line(monthly, x="Month", y="Sales_Count", markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Furnishing Status vs Average Price")
furn = filtered.groupby("Furnishing_Status", as_index=False)["Price"].mean()
fig = px.bar(furn, x="Furnishing_Status", y="Price", color="Furnishing_Status")
st.plotly_chart(fig, use_container_width=True)
