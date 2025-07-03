import streamlit as st
from components.CrudTable import *
from components.Widgets import Divider
from models import Pop

st.title("Data Management")
st.caption("Review, Create, Edit and Delete your Fundamental Data")
Divider()

#######################################################################
# Selection
selection = [
    {"label": "Period Data", "value": Period},
    {"label": "Population Data", "value": Pop},
    {"label": "Party Data", "value": Party},
]
selected = st.segmented_control(
    "Select Data Type",
    selection,
    format_func=lambda x: x["label"],
    key="data_type_selection",
    selection_mode="single",
)
if not selected:
    st.warning("Please select a data type to manage.")
    st.stop()

#######################################################################
# CRUD Table
selected_model = selected["value"]
CrudTable(selected_model)
