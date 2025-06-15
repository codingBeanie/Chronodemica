import streamlit as st
from components.CrudTable import *
from models import Pop

st.title("Data Management")
st.caption("Review, Create, Edit and Delete your Fundamental Data")
st.divider()

#######################################################################
# Selection
selection = [
    {"label": "Period Data", "value": "Period"},
    {"label": "Population Data", "value": "Pop"},
    {"label": "Party Data", "value": "Party"},
]
selected = st.selectbox("Select Data Type", selection, format_func=lambda x: x["label"])

#######################################################################
# CRUD Table
selected_model = selected["value"]
CrudTable(selected_model)
