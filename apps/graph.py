import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import datetime as dt
import plotly.express as px


@st.cache(show_spinner=False)
def set_data(main_df):
    main_df2 = main_df[main_df.apply(lambda x: False if pd.isna(x['continent']) or str(x['location'])[0:3] == 'Low' else True, axis=1)]
    main_df['date'] = pd.to_datetime(main_df['date'])
    date_ = main_df['date'].drop_duplicates().apply(lambda x: x.date())
    loc = main_df2['location'].drop_duplicates().sort_values()
    add_loc = pd.Series(['All Locations', 'Israel', 'United States'])
    loc = add_loc.append(loc, ignore_index= True)
    return main_df, date_.sort_values(), loc

@st.cache(show_spinner=False)
def df_loc_handle(df, user_loc):
    if user_loc == 'All Locations':
        return df[df['iso_code'] == 'OWID_WRL']
    con = df['location'] == user_loc
    return df[con]


@st.cache(show_spinner=False)
def df_date_handle(df, user_date, days_offset = 0):
    range_ = pd.date_range(user_date[0], user_date[1], freq='d')
    new_range = range_ + pd.Timedelta(days=days_offset)
    con = df['date'].apply(lambda x: True if x in range_ else False)
    new_con = df['date'].apply(lambda x: True if x in new_range else False)
    return df[con], df[new_con], range_, new_range


def fig_creator(user_input, df, new_df,  per_mil):
    offset = False
    lis = []
    string = 'new_cases_smoothed'
    for i in user_input:
        if offset:
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

        #df = df.groupby('id').mean()
        if i == 'Restrictions Policy':
            ig = alt.Chart(df).mark_bar().encode(x='date', y='stringency_index')
            lis.append(fig)
        else:
            if per_mil:
                if i == 'Tests':
                    string += "_per_thousand"
                elif i == 'People Vaccinated':
                    string += '_per_hundred'
                else:
                    string += "_per_million"
            fig = alt.Chart(df).mark_bar().encode(x='date', y=string)
            lis.append(fig)
        offset = True
    return lis


def app(df_main):
    # ---------Design-------------
    st.header("Covid-19 spread over time - graphs")
    # function calling
    all_df_main, date_series, loc_series = set_data(df_main)

    col1, col2 = st.columns(2)
    with col1:
        # widgets
        date_to_filter = st.select_slider("Select date range (1): ", options=date_series,
                                         value=[date_series.min(), date_series.max()])
        #which data to look on
        option_lis = ['New Cases', 'New Deaths', 'Covid Intensive Care Patients', 'Covid Hospital Patients',
                      'People Vaccinated', 'Tests', 'Restrictions Policy']
        #time slider
        user_loc = st.selectbox("Which location (1): ", loc_series, index=0)
        user_input = st.multiselect("Which graphs to show (1): ", option_lis)#, default='New Cases'


        #date offset slider
        days_offset = st.slider('Change the time frame of the graphs (besides the first one) (1)'
                                , -30, 30, value=0)
        #per mil checkbox
        per_mil = st.checkbox("View data relatively (per million/thousand/hundred) (1)")

        #widget functions
        all_df = df_loc_handle(all_df_main, user_loc) #what do i do if there len(df) == 0
        all_df, new_df, range_, new_range = df_date_handle(all_df, date_to_filter, days_offset)
        # calling fig creator
        fig_lis = fig_creator(user_input, all_df, new_df, per_mil)


        len_lis = len(fig_lis)
        if len_lis > 0:
            col1.write(f'**graph date range: ({range_[0].date()}) to ({range_[-1].date()})')
            col1.altair_chart(fig_lis[0])
        if len(fig_lis) > 1:
            range_ = new_range
            for i in fig_lis[1:]:
                col1.write(
                    f'**graph date range: ({range_[0].date()}) to ({range_[-1].date()})')
                col1.altair_chart(i)

    with col2:
        # widgets
        date_to_filter = st.select_slider("Select date range (2): ", options=date_series,
                                          value=[date_series.min(), date_series.max()])
        # which data to look on
        option_lis = ['New Cases', 'New Deaths', 'Covid Intensive Care Patients', 'Covid Hospital Patients',
                      'People Vaccinated', 'Tests', 'Restrictions Policy']
        # time slider
        user_loc = st.selectbox("Which location (2): ", loc_series, index=0, key='loc2')
        user_input = st.multiselect("Which graphs to show (2): ", option_lis)  # , default='New Cases'

        # date offset slider
        days_offset = st.slider('Change the time frame of the graphs (besides the first one) (2)'
                                , -30, 30, value=0)
        # per mil checkbox
        per_mil = st.checkbox("View data relatively (per million/thousand/hundred) (2)")

        # widget functions
        all_df = df_loc_handle(all_df_main, user_loc)# what do i do if there len(df) == 0
        all_df, new_df, range_, new_range = df_date_handle(all_df, date_to_filter, days_offset)
        # calling fig creator
        fig_lis = fig_creator(user_input, all_df, new_df, per_mil)

        len_lis = len(fig_lis)
        if len_lis > 0:
            col2.write(f'**graph date range: ({range_[0].date()}) to ({range_[-1].date()})')
            col2.altair_chart(fig_lis[0])
        if len(fig_lis) > 1:
            range_ = new_range
            for i in fig_lis[1:]:
                col2.write(
                    f'**graph date range: ({range_[0].date()}) to ({range_[-1].date()})')
                col2.altair_chart(i)

    st.write('To view the data behind everything that is presented here, go to: ')
    st.write('https://github.com/owid/covid-19-data/tree/master/public/data#confirmed-cases')