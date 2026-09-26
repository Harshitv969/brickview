"""BrickView - SQL Queries page: all 30 business queries with live results."""
import streamlit as st
from db import run_query
from sql_queries import QUERIES

st.set_page_config(page_title="BrickView | SQL Queries", layout="wide", page_icon="🧮")

st.sidebar.title("🏠 BrickView")
st.title("🧮 SQL Queries")
st.caption("30 business queries across Property, Sales, Agent, and Buyer analysis.")

for category, qs in QUERIES.items():
    st.markdown(f"## {category}")
    for name, sql in qs.items():
        with st.expander(name):
            st.code(sql.strip(), language="sql")
            try:
                result = run_query(sql)
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"Query error: {e}")
