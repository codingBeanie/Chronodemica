import streamlit as st
from models import *
from db import *
from simulation import *
from components.Selections import *
from components.Widgets import Divider
from dataframes import *

st.title("Timeline Statistics")
st.caption("View detailed voting statistics over all time periods.")
########################################################################
