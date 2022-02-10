import streamlit as st
import pandas as pd
from apps import Map, Map_p, graph

# get data for everything
@st.cache(allow_output_mutation=True)
def get_data():
    return pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")

# main page design and control
st.set_page_config(layout="wide", page_title="Coronavirus Analysis App")
st.title("Coronavirus Analysis App")
df_main = get_data()

# Sidebar design and control

# select box sidebar
main_page_lis = ('Data Labs (interactive)', 'Other')
st.sidebar.title("Pages")
main_pages = st.sidebar.selectbox(label="Choose main focus", options=main_page_lis)
if main_pages == 'Data Labs (interactive)':
    page_lis = ('Maps lab', 'Maps lab (periods)', "Graphs lab")
else:
    page_lis = ('bla', 'bla')

# radio Button sidebar
page_radio = st.sidebar.radio("Sub Pages ", page_lis)
if page_radio == 'Maps lab':
    Map.app(df_main)
elif page_radio == 'Maps lab (periods)':
    Map_p.app(df_main)
elif page_radio == 'Graphs lab':
    graph.app(df_main)
else:
    st.write("# What's up?")

