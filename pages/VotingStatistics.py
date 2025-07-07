import streamlit as st
from models import *
from db import *
from simulation import *
from components.Selections import *
from components.Widgets import Divider
from dataframes import *
from components.GraphElection import GraphElection

st.title("Voting Statistics")
st.caption("View detailed voting statistics for the selected period.")
########################################################################
# Selection
selection = SelectionGroup()

########################################################################
# Population Votes
if selection.model == PopPeriod:
    pop_votes = df_pop_votes(
        selection.period["id"],
        selection.object["id"],
    )
    GraphElection(
        pop_votes,
        f"Voting Statistics for {selection.object['name']} in {selection.period['year']}",
        threshold=0,
    )

########################################################################
# Party Votes
if selection.model == PartyPeriod:
    party_votes = df_party_votes(
        selection.period["id"],
        selection.object["id"],
    )
    GraphElection(
        party_votes,
        f"Voting Statistics for {selection.object['name']} in {selection.period['year']}",
        threshold=0,
    )
