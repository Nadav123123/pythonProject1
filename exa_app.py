import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
from urllib.request import urlopen
import json
## ---------Design-------------
st.set_page_config(layout="wide")
st.title("Coronavirus Analysis App")
st.subheader("The spread of the virus over time")


@st.cache
def set_data():
    with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
        counties = json.load(response)
    all_df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
                         ,dtype={"iso_code": str})
    all_df.rename({'iso_code': 'id'}, axis=1, inplace=True)
    all_df['date'] = pd.to_datetime(all_df['date'])
    return all_df, counties

@st.cache
#function to get read of line which iso_code don't match location json
def loc_prep(counties, all_df):
  lis_out = []
  lis = counties['features']
  num = 0
  for i in lis:
    lis_out.append(lis[num]['id'])
    num += 1
  return all_df[all_df['id'].apply(lambda x : True if x in lis_out else False)]

@st.cache
#create time range of the data
def date_range(all_df):
    max_date = all_df['date'].max()
    min_date = all_df['date'].min()
    max_date = dt.date(max_date.year, max_date.month, max_date.day)
    min_date = dt.date(min_date.year, min_date.month, min_date.day)
    return min_date, max_date


#function calling
all_df, counties = set_data()
all_df = loc_prep(counties, all_df)
min_date, max_date = date_range(all_df)
date_to_filter = pd.to_datetime(st.slider('Date', min_date, max_date, step = dt.timedelta(days = 7)
                                , key = "date_slider", value = min_date))
df = all_df[all_df['date'] == date_to_filter]
fig = px.choropleth(df, geojson = counties, locations = 'id', color = 'new_cases_smoothed'
                ,labels={'new_cases_smoothed':'New Cases'})
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600, width=1500)
st.write(fig)