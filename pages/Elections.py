import streamlit as st
from plots.GraphPoliticalCompass import PoliticalCompass
from plots.GraphPopulationDistribution import GraphPopulationDistribution
from components.Widgets import Divider
from components.Selections import SelectionPeriod
from models import *
from db import *
from simulation import *
from plots.GraphSeating import GraphSeating
from components.Coalitions import coalitions
from plots.GraphElection import GraphElection
from plots.GraphStackedBarH import graph_stacked_bar_h
from dataframes import *
from components.PopVotingBehavior import pop_voting_behavior


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

# Check if election data already exists
election_data_exists = (
    get_entries(ElectionResult, filters={"period_id": selected_period["id"]}) != []
)


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
if not election_data_exists:
    st.warning(
        "No election data found for this period. Please create election data first."
    )
    st.stop()
########################################################################
# Display Election Results
Divider("Election Results")
election_results = df_election_results(selected_period["id"], misc_threshold=3.0)
GraphElection(
    election_results,
    f"Election Results for {selected_period['year']}",
    st.session_state.get("threshold", 5),
)

Divider("Seating Chart")
graph_seating = GraphSeating(selected_period["id"], st.session_state.get("rows", 5))

Divider("Government & Coalitions")
coalitions = coalitions(selected_period["id"])

Divider("Population Group Voting")
pop_voting_behavior = pop_voting_behavior(selected_period["id"])

########################################################################
