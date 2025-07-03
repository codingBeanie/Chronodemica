import streamlit as st
from components.GraphPoliticalCompass import PoliticalCompass
from components.GraphPopulationDistribution import GraphPopulationDistribution
from components.Widgets import Divider
from components.Selections import SelectionPeriod
from models import *
from db import *
from simulation import *
from components.GraphElectionResult import GraphElectionResult
from components.GraphSeating import GraphSeating
from components.Coalitions import Coalitions


#########################################################################
# functions
def create_election_data(period_id, seats, threshold):
    create_pop_votes(period_id)
    create_election_results(period_id, seats, threshold)


#########################################################################

st.title("Elections")
st.caption("Create an election simulation")

#######################################################################
# Select Period
periodSelection = SelectionPeriod()
selected_period = periodSelection.selected_period
if not selected_period:
    st.warning("Please select a period to continue.")
    st.stop()

#######################################################################
# Create or update election
with st.container(border=True):
    cols = st.columns(3)
    cols[0].number_input(
        "Parliament Seats",
        key="seats",
        min_value=1,
        step=1,
        value=150,
    )
    cols[1].number_input(
        "Threshold to enter Parliament (%)",
        key="threshold",
        min_value=0,
        max_value=100,
        step=1,
        value=5,
    )
    cols[2].number_input(
        "Rows in Parliament",
        key="rows",
        min_value=1,
        step=1,
        value=5,
    )
    st.button(
        "Create or Update Election Data",
        type="primary",
        use_container_width=False,
        on_click=lambda: create_election_data(
            selected_period["id"],
            st.session_state.get("seats", 100),
            st.session_state.get("threshold", 5),
        ),
    )

########################################################################
# Display Election Results
Divider("Election Results")
graph_election_result = GraphElectionResult(
    selected_period["id"],
    st.session_state.get("threshold", 5),
)

Divider("Seating Chart")
graph_seating = GraphSeating(selected_period["id"], st.session_state.get("rows", 5))

Divider("Government & Coalitions")
coalitions = Coalitions(selected_period["id"])

########################################################################
