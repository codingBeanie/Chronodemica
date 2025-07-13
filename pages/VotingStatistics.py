import streamlit as st
from models import *
from db import *
from simulation import *
from components.Selections import *
from components.Widgets import Divider
from dataframes import *
from plots.GraphElection import GraphElection

st.title("Voting Statistics")
st.caption("View detailed voting statistics for the selected period.")
########################################################################
# Selection
selection = SelectionGroup(show_object_selection=False)

########################################################################
# Pop Data
if selection.model == PopPeriod:
    pop_votes = df_pop_votes(selection.period["id"])
    st.write(pop_votes)
