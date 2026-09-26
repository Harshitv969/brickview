"""
Shared SQLite connection helper used by every page.
Enables foreign key enforcement so, e.g., deleting an agent who still has
listings will raise an IntegrityError instead of silently orphaning rows.
"""
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "brickview.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def run_query(sql, params=None):
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def run_write(sql, params=None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()


@st.cache_data(ttl=300)
def load_listing_full():
    df = run_query("SELECT * FROM v_listing_full")
    df["Listed_Date"] = pd.to_datetime(df["Listed_Date"])
    return df


@st.cache_data(ttl=300)
def load_sales_full():
    df = run_query("SELECT * FROM v_sales_full")
    df["Sale_Date"] = pd.to_datetime(df["Sale_Date"])
    return df
