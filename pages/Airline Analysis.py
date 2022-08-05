import streamlit as st 
import snowflake.connector 
import pandas as pd
import datetime as dt

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

st.subheader("Total Airline Departure Trends per Day in a Month")
country = pd.read_sql_query("SELECT DISTINCT(DEPCTRY) from AIRLINE.PUBLIC.OAG_SCHEDULE;", conn)
choice = st.selectbox("Country", country)

city = pd.read_sql_query("SELECT DISTINCT(DEPCITY) from AIRLINE.PUBLIC.OAG_SCHEDULE WHERE DEPCTRY = " + "\'" + choice + "\'" + ";", conn)
cityChoice = st.selectbox("City", city)

data = pd.read_sql_query("SELECT COUNT(DEPCITY) AS CD, FLIGHT_DATE FROM AIRLINE.PUBLIC.OAG_SCHEDULE WHERE DEPCTRY = " + "\'" + choice + "\'" + " AND DEPCITY = " + "\'" + cityChoice + "\'" + " GROUP BY FLIGHT_DATE;", conn)

distance = pd.read_sql_query("SELECT SUM(DISTANCE) AS DISTANCE, FLIGHT_DATE " +
"FROM AIRLINE.PUBLIC.OAG_SCHEDULE " +
"WHERE DEPCTRY = " + "\'" + choice + "\'" + " AND DEPCITY = " + "\'" + cityChoice + "\'" + "GROUP BY FLIGHT_DATE;", conn)

minData = pd.read_sql_query("SELECT MIN(CD) as MCD, FLIGHT_DATE FROM " +
"(SELECT COUNT(DEPCITY)AS CD, FLIGHT_DATE FROM AIRLINE.PUBLIC.OAG_SCHEDULE " +
"WHERE DEPCTRY = " + "\'" + choice + "\'" + " AND DEPCITY =" + "\'" + cityChoice + "\'" " GROUP BY FLIGHT_DATE) " +
" WHERE FLIGHT_DATE LIKE \'2023%\' GROUP BY FLIGHT_DATE ORDER BY MCD;", conn)

# enumerate returns the key-value pairs for EACH FLIGHT_DATE
for i, val in enumerate(data['FLIGHT_DATE']):
    data['FLIGHT_DATE'].iloc[i] = data['FLIGHT_DATE'].iloc[i].strftime('%B-%Y')

for i, val in enumerate(distance['FLIGHT_DATE']):
    distance['FLIGHT_DATE'].iloc[i] = distance['FLIGHT_DATE'].iloc[i].strftime('%B-%Y')

for i, val in enumerate(minData['FLIGHT_DATE']):
    minData['FLIGHT_DATE'].iloc[i] =  minData['FLIGHT_DATE'].iloc[i].strftime('%B-%Y')

airlineData = pd.DataFrame({
  'Total Flights for ' + cityChoice: data['CD'],
  'Flight Date' : data['FLIGHT_DATE']
})

distanceData = pd.DataFrame({
  'Total Distance Traveled for ' + cityChoice: distance['DISTANCE'],
  'Flight Date' : distance['FLIGHT_DATE']
})

minimumData = pd.DataFrame({
  'Minimum Departures for ' + cityChoice: minData['MCD'],
  'Flight Date' : minData['FLIGHT_DATE']
})

airlineData = airlineData.rename(columns={'Flight Date':'index'}).set_index('index')
distancePlot = distanceData.rename(columns={'Flight Date':'index'}).set_index('index')
minPlot = minimumData.rename(columns={'Flight Date':'index'}).set_index('index')

st.bar_chart(airlineData, use_container_width=True)

with st.expander("View Minimum Flight Departures"):
    st.bar_chart(minPlot,  use_container_width=True)

with st.expander("View Total Distance"):
    st.bar_chart(distancePlot,  use_container_width=True)