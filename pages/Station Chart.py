
import streamlit as st 
import snowflake.connector 
import pandas as pd
import datetime
import time
import numpy as np

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
location = pd.read_sql_query("SELECT DISTINCT ROUND( \"Station Latitude\", 8) AS lat, ROUND(\"Station Longitude\", 8) AS lon from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)

location = location.rename(columns={'LAT':'lat'})
location = location.rename(columns={'LON':'lon'})

st.header("Weather Station Maps")
st.map(location)