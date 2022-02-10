import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
from urllib.request import urlopen
import json


@st.cache(show_spinner=False)
def set_data(main_df):
    with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
        counties = json.load(response)
    all_df = main_df.rename({'iso_code': 'id'}, axis=1, inplace=False)
    all_df['date'] = pd.to_datetime(all_df['date'])
    lis_out = []
    lis = counties['features']
    num = 0
    for i in lis:
        lis_out.append(lis[num]['id'])
        num += 1
    all_df = all_df[all_df['id'].apply(lambda x : True if x in lis_out else False)]
    date_ = all_df['date'].drop_duplicates().apply(lambda x: x.date())
    all_df.fillna(0, inplace=True)
    return all_df, counties, date_.sort_values()

def df_time_offset(df, new_range):
    con = df['date'].apply(lambda x: True if x in new_range else False)
    return df[con]

def another_fig(user_input, df, geo, user_date, per_mil, days_offset = 0):
    ofsset = False
    range_ = pd.date_range(user_date[0], user_date[1], freq='d')
    new_range = range_ + pd.Timedelta(days= days_offset)
    new_df = df_time_offset(df, new_range)
    con = df['date'].apply(lambda x: True if x in range_ else False)
    df = df[con]
    lis = []
    string = 'new_cases_smoothed'
    for i in user_input:
        if ofsset:
            if len(new_df) == 0:
                st.warning("Date offset slider create out of range values, treating it as zero")
            else:
                df = new_df
        if i == 'New Cases':
            string = 'new_cases'

        elif i == 'New Deaths':
            string = 'new_deaths'

        elif i == 'Covid Intensive Care Patients':
            string = 'icu_patients'

        elif i == 'Covid Hospital Patients':
            string = 'hosp_patients'

        elif i == 'People Vaccinated':
            string = 'people_vaccinated'

        elif i == 'Tests':
            string = 'new_tests'

        df = df.groupby('id').mean()
        if i == 'Restrictions Policy':
            fig = px.choropleth(df, geojson=geo, locations=df.index, color='stringency_index'
                                , labels={'stringency_index': 'Restrictions Level'}
                                , range_color=[0, 100])
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600, width=1500)
            lis.append(fig)
        else:
            if per_mil:
                if i == 'Tests':
                    string += "_per_thousand"
                elif i == 'People Vaccinated':
                    string += '_per_hundred'
                else:
                    string += "_per_million"
            fig = px.choropleth(df, geojson=geo, locations=df.index, color=string
                                , labels={string: i})
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600, width=1500)
            lis.append(fig)
        ofsset = True
    return lis, range_, new_range

def app(df_main):
    # ---------Design-------------
    st.header("Covid-19 spread over time - map")

    # function calling
    all_df, counties, date_series = set_data(df_main)

    # widgets
    st.write("**The data shown below is for 7 days at a time (summarize of new cases of 7 days from the day chosen)")
    option_lis = ['New Cases', 'New Deaths', 'Covid Intensive Care Patients', 'Covid Hospital Patients',
                  'People Vaccinated', 'Tests', 'Restrictions Policy']
    user_input = st.multiselect("Which maps to show: ", option_lis)
    date_to_filter = st.select_slider("Select date range: ", options=date_series,
                                      value=[date_series.min(), date_series.max()])
    days_offset = st.slider('Days offset - changing the time frame of the maps (besides the first one)'
                            , -30, 30, value=0, key = 'days_offset')
    per_mil = st.checkbox("View data relatively (per million/thousand/hundred)")

    # calling fig creator
    fig_lis, range_, new_range = another_fig(user_input, all_df, counties, date_to_filter, per_mil, days_offset)
    len_lis = len(fig_lis)
    if len_lis > 0:
        st.write(f'**map date range: ({range_[0].date()}) to ({range_[-1].date()})'
                f', the data shown is an average for the time period')
        st.write(fig_lis[0])
    if len(fig_lis) > 1:
        range_ = new_range
        for i in fig_lis[1:]:
            st.write(
                f'**map date range: ({range_[0].date()}) to ({range_[-1].date()})'
                f', the data shown is an average for the time period')
            st.write(i)

    st.write('To view the data behind everything that is presented here, go to: ')
    st.write('https://github.com/owid/covid-19-data/tree/master/public/data#confirmed-cases')