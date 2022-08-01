# streamlit_app.py 

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


# GET SEPARATE PRECIP AND TEMP DATA WITH TIME
options = pd.read_sql_query("SELECT DISTINCT \"Country\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\";", conn)
choice = st.selectbox("Choose a country", options)
with st.spinner(text='In progress'):
  time.sleep(2)
  st.success("Data for "+ choice + " loaded successfully!")

precipData = pd.read_sql_query("SELECT \"Precipitation, Total\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + ";", conn)
tempData = pd.read_sql_query("SELECT \"Temperature, Mean (°C)\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + ";", conn)
time = pd.read_sql_query("SELECT \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + ";", conn)

precip = pd.DataFrame({
  'date': time['Time'],
  'Precipitation': precipData['Precipitation, Total']
})
precip = precip.rename(columns={'date':'index'}).set_index('index')
st.header("Total Precipitation vs. Time in " + choice)
st.line_chart(precip)

temp = pd.DataFrame({
  'date': time['Time'],
  'Temperature in °C': tempData['Temperature, Mean (°C)']
})
temp = temp.rename(columns={'date':'index'}).set_index('index')
st.header("Average Temperature vs. Time in " + choice)
st.line_chart(temp)

# READ LATITUDE & LONGITUDE
location = pd.read_sql_query("SELECT DISTINCT (\"Station Latitude\", \"Station Longitude\") from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)

location = location.rename(columns={'Station Latitude':'lat'})
location = location.rename(columns={'Station Longitude':'lon'})
print(location.to_numpy)

st.dataframe(location)
st.header("Test Map")
st.map(location)

# x = np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4]
# print(x)