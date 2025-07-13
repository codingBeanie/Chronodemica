import streamlit as st
from plots.GraphPoliticalCompass import PoliticalCompass
from plots.GraphPopulationDistribution import GraphPopulationDistribution
from components.Widgets import Divider
from components.Selections import SelectionPeriod
from models import *

#########################################################################

st.title("Data Visualisation")
st.caption("Visualisation of your periodic data")

#######################################################################
# Select Period
periodSelection = SelectionPeriod()
selected_period = periodSelection.selected_period

#######################################################################
Divider("Political Compass")
if selected_period:
    political_compass = PoliticalCompass(selected_period["id"])
else:
    st.info("Please select a period to view the political compass.")

#####################################################################
Divider("Population Distribution")
if selected_period:
    population_distribution = GraphPopulationDistribution(selected_period["id"])
else:
    st.info("Please select a period to view the population distribution.")
#####################################################################
