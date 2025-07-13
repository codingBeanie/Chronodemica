import streamlit as st
from db import *

# init DB
init_db()

st.set_page_config(page_title="Chronodemica", page_icon="logo.png", layout="wide")

###########################################################################
pages = [
    st.Page("pages/FundamentalData.py", title="Fundamental Data"),
    st.Page("pages/PeriodicDetails.py", title="Periodic Details"),
    st.Page("pages/Elections.py", title="Elections"),
    st.Page("pages/Timeline.py", title="Timeline Statistics"),
]

navigation = st.navigation(pages)
navigation.run()
##########################################################################
