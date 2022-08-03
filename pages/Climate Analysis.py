import streamlit as st 
import snowflake.connector 
import pandas as pd
import datetime
import time
import numpy as np
from sklearn.linear_model import LinearRegression

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
  time.sleep(1)
  st.snow() 
  st.success("Data for "+ choice + " loaded successfully!")

precipData = pd.read_sql_query("SELECT MAX(\"Precipitation, Total\") as \"Precipitation, Total\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)
tempData = pd.read_sql_query("SELECT MAX(\"Temperature, Mean (°C)\") as \"Temperature, Mean (°C)\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)
sunData = pd.read_sql_query("SELECT MAX(\"Sunshine, Total\") as \"Sunshine, Total\"  from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)
time = pd.read_sql_query("SELECT \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + ";", conn)

# LINEAR REGRESSION QUERY
precipAndTime = pd.read_sql_query("SELECT MAX(\"Precipitation, Total\") as \"Precipitation, Total\", \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)
tempAndTime = pd.read_sql_query("SELECT MAX(\"Temperature, Mean (°C)\") as \"Temperature, Mean (°C)\", \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)
sunAndTime = pd.read_sql_query("SELECT MAX(\"Sunshine, Total\") as \"Sunshine, Total\", \"Time\" from WEATHER.KNMCD_DATA_PACK.\"zdqkepg\" where \"Country\" = " + "\'" + choice + "\'" + "GROUP BY \"Time\";", conn)

# SUNSHINE ANALYSIS
sun = pd.DataFrame({
  'Date': time['Time'],
  'Sunshine Total': sunData['Sunshine, Total'],
})

sun = sun.rename(columns={'Date':'index'}).set_index('index')
st.subheader("Max Total Sunshine vs Time (per day) in " + choice)
st.bar_chart(sun)

# LINEAR REGRESSION OF SUNSHINE
sunRes = pd.DataFrame({
  'date': sunAndTime['Time'],
  'Sunshine Total': sunAndTime['Sunshine, Total']
})

sunRes['date'] = pd.to_datetime(sunRes['date']).apply(lambda date: date.toordinal())


index = sunRes.loc[pd.isna(sunRes['Sunshine Total']), :].index
X = sunRes.loc[:, ['date']].drop(index) # features
y = sunRes.loc[:, ['Sunshine Total']].dropna() # target

model = LinearRegression()
model.fit(X, y)

timeDropped = sunAndTime['Time'].drop(index)
sun_pred = pd.DataFrame(model.predict(X), timeDropped, columns= ["Sunshine Total"])

with st.expander("View Linear Regression Model for Max Total Sunshine"):
  st.subheader("Linear Regression of Max Total Sunshine in " + choice)
  st.line_chart(sun_pred)


# PRECIPITATION ANALYSIS
precip = pd.DataFrame({
  'Date': time['Time'],
  'Precipitation Total (mm)': precipData['Precipitation, Total'],
})

precip = precip.rename(columns={'Date':'index'}).set_index('index')
st.subheader("Max Total Precipitation vs. Time (per day) in " + choice)
st.bar_chart(precip)

# LINEAR REGRESSION OF PRECIPITATION
precipRes = pd.DataFrame({
  'date': precipAndTime['Time'],
  'Precipitation Total (mm)': precipAndTime['Precipitation, Total']
})

precipRes['date'] = pd.to_datetime(precipRes['date']).apply(lambda date: date.toordinal())


index = precipRes.loc[pd.isna(precipRes["Precipitation Total (mm)"]), :].index
X = precipRes.loc[:, ['date']].drop(index) # features
y = precipRes.loc[:, ['Precipitation Total (mm)']].dropna() # target

model = LinearRegression()
model.fit(X, y)

timeDropped = precipAndTime['Time'].drop(index)
precip_pred = pd.DataFrame(model.predict(X), timeDropped, columns= ["Preciptation Total (mm)"])

with st.expander("View Linear Regression Model for Max Total Precipitation"):
  st.subheader("Linear Regression of Max Total Precipitation in " + choice)
  st.line_chart(precip_pred)

# TEMPERATURE ANALYSIS
temp = pd.DataFrame({
  'date': time['Time'],
  'Temperature in °C': tempData['Temperature, Mean (°C)']
})
temp = temp.rename(columns={'date':'index'}).set_index('index')
st.subheader("Max Average Temperature vs. Time (per day) in " + choice)
st.bar_chart(temp)

# LINEAR REGRESSION OF TEMPERATURE
tempRes = pd.DataFrame({
  'date': tempAndTime['Time'],
  'Temperature': tempAndTime['Temperature, Mean (°C)']
})

tempRes['date'] = pd.to_datetime(tempRes['date']).apply(lambda date: date.toordinal())


index = tempRes.loc[pd.isna(tempRes["Temperature"]), :].index
X = tempRes.loc[:, ['date']].drop(index) # features
y = tempRes.loc[:, ['Temperature']].dropna() # target

model = LinearRegression()
model.fit(X, y)

timeDropped = precipAndTime['Time'].drop(index)
temp_pred = pd.DataFrame(model.predict(X), timeDropped, columns= ["Temperature in °C"])

with st.expander("View Linear Regression Model for Max Average Temperature"):
  st.subheader("Linear Regression of Max Average Temperature in " + choice)
  st.line_chart(temp_pred)