"""BrickView - Interactive Property Location Map with marker clustering."""
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from filters import render_filters

st.set_page_config(page_title="BrickView | Map", layout="wide", page_icon="🗺️")

st.sidebar.title("🏠 BrickView")
filtered = render_filters()

st.title("🗺️ Property Location Map")

if len(filtered) == 0:
    st.warning("No listings match the current filters — adjust filters in the sidebar.")
    st.stop()

max_points = st.slider("How many listings to show on the map?", 50, min(2000, len(filtered)),
                        min(500, len(filtered)), step=50)

sample = filtered.sample(n=min(max_points, len(filtered)), random_state=1)
st.caption(f"Showing {len(sample):,} of {len(filtered):,} filtered listings (grouped into clusters for readability).")

center_lat = sample["Latitude"].mean()
center_lon = sample["Longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="OpenStreetMap")
cluster = MarkerCluster().add_to(m)

for _, row in sample.iterrows():
    popup_html = (
        f"<b>{row['Listing_ID']}</b><br>"
        f"{row['Property_Type']} in {row['City']}<br>"
        f"${row['Price']:,.0f} · {row['Area_sqft']} sqft<br>"
        f"Agent: {row['Agent_Name']}"
    )
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=row["Listing_ID"],
    ).add_to(cluster)

st_folium(m, use_container_width=True, height=600, returned_objects=[])
