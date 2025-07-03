import streamlit as st
from db import *

# init DB
init_db()

st.set_page_config(page_title="Chronodemica", page_icon="logo.png", layout="wide")

###########################################################################
pages = {
    "Data Entry": [
        st.Page("pages/FundamentalData.py", title="Fundamental Data"),
        st.Page("pages/PeriodicDetails.py", title="Periodic Details"),
    ],
    "Simulation": [
        st.Page("pages/Elections.py", title="Elections"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
##########################################################################
