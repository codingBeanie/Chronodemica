import streamlit as st
from db import *

# init DB
init_db()

st.set_page_config(page_title="Chronodemica", page_icon="⏳")

###########################################################################
pages = {
    "Data Entry": [
        st.Page("pages/FundamentalData.py", title="Fundamental Data"),
    ],
    "Simulation": [],
}
navigation = st.navigation(pages)
navigation.run()
##########################################################################
