"""
Shared sidebar filters. Uses st.session_state so selections persist as the
user navigates between pages in the multi-page app (Streamlit does not share
widget state across pages by default unless keys are stable, which these are).
"""
import streamlit as st
from db import load_listing_full


def render_filters():
    df = load_listing_full()

    st.sidebar.subheader("Global Filters")

    cities = sorted(df["City"].dropna().unique())
    ptypes = sorted(df["Property_Type"].dropna().unique())
    agents_list = sorted(df["Agent_Name"].dropna().unique())

    sel_cities = st.sidebar.multiselect("City", cities, default=[], key="f_cities")
    sel_ptypes = st.sidebar.multiselect("Property Type", ptypes, default=[], key="f_ptypes")

    price_min, price_max = int(df["Price"].min()), int(df["Price"].max())
    sel_price = st.sidebar.slider(
        "Price Range ($)", price_min, price_max, (price_min, price_max), key="f_price"
    )

    sel_agent = st.sidebar.selectbox("Agent", ["All"] + agents_list, key="f_agent")

    date_min, date_max = df["Listed_Date"].min(), df["Listed_Date"].max()
    sel_dates = st.sidebar.date_input(
        "Listed Date Range", (date_min, date_max), key="f_dates"
    )

    if st.sidebar.button("Reset Filters"):
        for k in ["f_cities", "f_ptypes", "f_price", "f_agent", "f_dates"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    out = df.copy()
    if sel_cities:
        out = out[out["City"].isin(sel_cities)]
    if sel_ptypes:
        out = out[out["Property_Type"].isin(sel_ptypes)]
    out = out[(out["Price"] >= sel_price[0]) & (out["Price"] <= sel_price[1])]
    if sel_agent != "All":
        out = out[out["Agent_Name"] == sel_agent]
    if isinstance(sel_dates, tuple) and len(sel_dates) == 2:
        import pandas as pd
        out = out[(out["Listed_Date"] >= pd.Timestamp(sel_dates[0])) &
                  (out["Listed_Date"] <= pd.Timestamp(sel_dates[1]))]

    return out
