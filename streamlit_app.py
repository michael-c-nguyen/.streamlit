# streamlit_app.py 

import streamlit as st 
import snowflake.connector 
import pandas as pd
import datetime

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

#TEMP AND PRECIP ON A SINGlE GRAPH
# data = pd.read_sql_query("SELECT \"Precipitation, Total\" as \"Total Precipitation\", \"Temperature, Mean (°C)\" as \"Average Temperature\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)
# st.title("Total Precipitation and Average Temperature in the United States")
# st.line_chart(data, use_container_width=True) 
# st.dataframe(data)t

# GET SEPARATE PRECIP AND TEMP DATA WITH TIME
precipData = pd.read_sql_query("SELECT \"Precipitation, Total\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)
tempData = pd.read_sql_query("SELECT \"Temperature, Mean (°C)\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)
time = pd.read_sql_query("SELECT \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)

precip = pd.DataFrame({
  'date': time['Time'],
  'Precipitation': precipData['Precipitation, Total']
})
precip = precip.rename(columns={'date':'index'}).set_index('index')
st.title("Total Precipitation vs. Time in the US")
st.line_chart(precip)

temp = pd.DataFrame({
  'date': time['Time'],
  'Temperature in °C': tempData['Temperature, Mean (°C)']
})
temp = temp.rename(columns={'date':'index'}).set_index('index')
st.title("Average Temperature vs. Time in the US")
st.line_chart(temp)

# READ LATITUDE & LONGITUDE
# lat = pd.read_sql_query("SELECT \"Station Latitude\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)
# lon = pd.read_sql_query("SELECT \"Station Longitude\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = 'USA';", conn)


# Print results. 

# for row in tempData: 
#     st.write(f"{row[0]} Temperature: {row[1]}")
