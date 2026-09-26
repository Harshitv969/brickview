"""
BrickView - CRUD Operations page.
Proper type casting (no more raw strings into SQLite), FK existence checks,
and required-field validation before writing.
"""
import datetime
import streamlit as st
from db import run_query, run_write, get_conn

st.set_page_config(page_title="BrickView | CRUD", layout="wide", page_icon="📝")
st.sidebar.title("🏠 BrickView")
st.title("📝 CRUD Operations")

# Column schema: (dtype, widget, extra) — dtype in {str, int, float, bool, date}
# extra: for 'select' widgets, a list of choices; for FK, the (table, column) to validate against
SCHEMA = {
    "listings": {
        "pk": "Listing_ID",
        "columns": {
            "Listing_ID": ("str", None),
            "City": ("str", None),
            "Property_Type": ("select", ["Apartment", "Villa", "Condo", "Townhouse", "Farmhouse"]),
            "Price": ("float", None),
            "Area_sqft": ("int", None),
            "Price_per_sqft": ("float", None),
            "Agent_ID": ("fk", ("agents", "Agent_ID")),
            "Listed_Date": ("date", None),
            "Latitude": ("float", None),
            "Longitude": ("float", None),
        },
    },
    "property_attributes": {
        "pk": "Attribute_ID",
        "columns": {
            "Attribute_ID": ("str", None),
            "Listing_ID": ("fk", ("listings", "Listing_ID")),
            "Bedrooms": ("int", None),
            "Bathrooms": ("int", None),
            "Floor_Number": ("int", None),
            "Total_Floors": ("int", None),
            "Year_Built": ("int", None),
            "Is_Rented": ("bool", None),
            "Tenant_Count": ("int", None),
            "Furnishing_Status": ("select", ["Furnished", "Semi-Furnished", "Unfurnished"]),
            "Metro_Distance_Km": ("float", None),
            "Parking_Available": ("bool", None),
            "Power_Backup": ("bool", None),
        },
    },
    "agents": {
        "pk": "Agent_ID",
        "columns": {
            "Agent_ID": ("str", None),
            "Name": ("str", None),
            "City": ("str", None),
            "Contact": ("str", None),
            "Commission_Rate": ("float", None),
            "Deals_Closed": ("int", None),
            "Rating": ("float", None),
            "Experience_Years": ("int", None),
            "Avg_Closing_Days": ("int", None),
        },
    },
    "sales": {
        "pk": "Sale_ID",
        "columns": {
            "Sale_ID": ("str", None),
            "Listing_ID": ("fk", ("listings", "Listing_ID")),
            "Sale_Date": ("date", None),
            "Sale_Price": ("float", None),
            "Days_On_Market": ("int", None),
        },
    },
    "buyers": {
        "pk": "Buyer_ID",
        "columns": {
            "Buyer_ID": ("str", None),
            "Sale_ID": ("fk", ("sales", "Sale_ID")),
            "Buyer_Type": ("select", ["Investor", "End User"]),
            "Payment_Mode": ("select", ["Cash", "UPI", "Bank Transfer", "Cheque"]),
            "Loan_Taken": ("bool", None),
            "Loan_Provider": ("str", None),
            "Loan_Amount": ("float", None),
        },
    },
}


def cast_value(dtype, raw):
    """Cast a raw widget value to the correct Python/SQLite type."""
    if dtype in ("int",):
        return int(raw)
    if dtype in ("float",):
        return float(raw)
    if dtype == "bool":
        return int(bool(raw))
    if dtype == "date":
        return raw.strftime("%Y-%m-%d") if isinstance(raw, (datetime.date, datetime.datetime)) else str(raw)
    return raw  # str, select, fk all stay as-is (strings)


def fk_exists(table, column, value):
    df = run_query(f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1", (value,))
    return len(df) > 0


def render_input(label, dtype, extra, default=None, key=None):
    if dtype == "int":
        return st.number_input(label, value=int(default) if default not in (None, "") else 0,
                                 step=1, key=key)
    if dtype == "float":
        return st.number_input(label, value=float(default) if default not in (None, "") else 0.0,
                                 step=0.01, format="%.2f", key=key)
    if dtype == "bool":
        val = default
        if isinstance(val, str):
            val = val in ("1", "True", "true")
        return st.checkbox(label, value=bool(val) if val is not None else False, key=key)
    if dtype == "date":
        try:
            val = datetime.datetime.strptime(str(default), "%Y-%m-%d").date() if default else datetime.date.today()
        except ValueError:
            val = datetime.date.today()
        return st.date_input(label, value=val, key=key)
    if dtype == "select":
        idx = extra.index(default) if default in extra else 0
        return st.selectbox(label, extra, index=idx, key=key)
    if dtype == "fk":
        table, col = extra
        options = run_query(f"SELECT {col} FROM {table}")[col].astype(str).tolist()
        idx = options.index(str(default)) if default is not None and str(default) in options else 0
        return st.selectbox(f"{label} (FK → {table}.{col})", options, index=idx, key=key) if options else None
    return st.text_input(label, value=str(default) if default is not None else "", key=key)


table = st.selectbox("Select table", list(SCHEMA.keys()))
schema = SCHEMA[table]
pk = schema["pk"]
columns = schema["columns"]

tab_view, tab_add, tab_update, tab_delete = st.tabs(["View", "Add", "Update", "Delete"])

with tab_view:
    df = run_query(f"SELECT * FROM {table}")
    st.dataframe(df, use_container_width=True, height=420)
    st.caption(f"{len(df):,} rows")

with tab_add:
    st.write(f"Add a new row to **{table}**")
    with st.form(f"add_{table}", clear_on_submit=True):
        raw_values = {}
        for col, (dtype, extra) in columns.items():
            raw_values[col] = render_input(col, dtype, extra, default=None, key=f"add_{table}_{col}")
        submitted = st.form_submit_button("Add Record")
        if submitted:
            errors = []
            if not raw_values.get(pk):
                errors.append(f"{pk} is required.")
            for col, (dtype, extra) in columns.items():
                if dtype == "fk" and extra:
                    ftable, fcol = extra
                    if raw_values[col] and not fk_exists(ftable, fcol, raw_values[col]):
                        errors.append(f"{col} '{raw_values[col]}' does not exist in {ftable}.{fcol}.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    cast = {c: cast_value(columns[c][0], v) for c, v in raw_values.items()}
                    cols_sql = ", ".join(cast.keys())
                    placeholders = ", ".join(["?"] * len(cast))
                    run_write(f"INSERT INTO {table} ({cols_sql}) VALUES ({placeholders})",
                               tuple(cast.values()))
                    st.success(f"Record added to {table}.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Database error: {e}")

with tab_update:
    df = run_query(f"SELECT * FROM {table}")
    ids = df[pk].astype(str).tolist()
    sel_id = st.selectbox(f"Select {pk} to update", ids, key=f"upd_sel_{table}") if ids else None
    if sel_id:
        row = df[df[pk].astype(str) == sel_id].iloc[0]
        with st.form(f"update_{table}"):
            raw_values = {}
            for col, (dtype, extra) in columns.items():
                if col == pk:
                    st.text_input(col, value=str(row[col]), disabled=True)
                    raw_values[col] = row[col]
                else:
                    raw_values[col] = render_input(col, dtype, extra, default=row[col],
                                                     key=f"upd_{table}_{col}")
            submitted = st.form_submit_button("Update Record")
            if submitted:
                errors = []
                for col, (dtype, extra) in columns.items():
                    if dtype == "fk" and extra and col != pk:
                        ftable, fcol = extra
                        if raw_values[col] and not fk_exists(ftable, fcol, raw_values[col]):
                            errors.append(f"{col} '{raw_values[col]}' does not exist in {ftable}.{fcol}.")
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        cast = {c: cast_value(columns[c][0], v) for c, v in raw_values.items() if c != pk}
                        set_clause = ", ".join([f"{c} = ?" for c in cast])
                        run_write(f"UPDATE {table} SET {set_clause} WHERE {pk} = ?",
                                   tuple(cast.values()) + (sel_id,))
                        st.success(f"Record {sel_id} updated.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Database error: {e}")

with tab_delete:
    df = run_query(f"SELECT * FROM {table}")
    ids = df[pk].astype(str).tolist()
    del_id = st.selectbox(f"Select {pk} to delete", ids, key=f"del_sel_{table}") if ids else None
    if del_id:
        st.warning(f"This will permanently delete {pk} = {del_id} from {table}.")
        if st.button("Delete Record", type="primary", key=f"del_btn_{table}"):
            try:
                run_write(f"DELETE FROM {table} WHERE {pk} = ?", (del_id,))
                st.success(f"Record {del_id} deleted.")
                st.cache_data.clear()
            except Exception as e:
                st.error(
                    f"Could not delete: {e}. This usually means other rows "
                    f"still reference this record (foreign key constraint)."
                )
