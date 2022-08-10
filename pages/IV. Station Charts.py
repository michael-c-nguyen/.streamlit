
import streamlit as st 
import snowflake.connector 
import pandas as pd
import datetime
import time
import numpy as np
import pydeck as pdk

# Initialize connection. 

# Uses st.experimental_singleton to only run once. 

@st.experimental_singleton 

def init_connection(): 
    return snowflake.connector.connect(**st.secrets["snowflake"]) 

conn = init_connection() 


# Perform query. 

# Uses st.experimental_memo to only rerun when the query changes or after 10 min. 

@st.experimental_memo(ttl=600) 

def run_query(query): 

    with conn.cursor() as cur: 
        cur.execute(query) 
        return cur.fetchall() 

# READ LATITUDE & LONGITUDE
location = pd.read_sql_query("SELECT ROUND( \"Station Latitude\", 8) AS lat, ROUND(\"Station Longitude\", 8) AS lon from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)
locationDistinct = pd.read_sql_query("SELECT DISTINCT ROUND( \"Station Latitude\", 8) AS lat, ROUND(\"Station Longitude\", 8) AS lon from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)

location = location.rename(columns={'LAT':'lat'})
location = location.rename(columns={'LON':'lon'})

locationDistinct = location.rename(columns={'LAT':'lat'})
locationDistinct = location.rename(columns={'LON':'lon'})

st.subheader("Weather Station Maps")
st.map(locationDistinct)

st.subheader("Weather Stations as a Stack Deck")
st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude=37.76,
         longitude=-122.4,
         zoom=9,
         pitch=50,
     ),
     layers=[
         pdk.Layer(
            'HexagonLayer',
            data=location,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
         ),
         pdk.Layer(
             'ScatterplotLayer',
             data=location,
             get_position='[lon, lat]',
             get_color='[200, 30, 0, 160]',
             get_radius=200,
         ),
     ],
 ))