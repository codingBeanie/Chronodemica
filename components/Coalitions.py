import streamlit as st
from db import *
from models import *
from simulation import *
import pandas as pd
import itertools
from dataframes import *
from plots.GraphHorizontalStackedBar import GraphHorizontalStackedBar


def coalitions(period_id):
    st.write("## Government & Coalitions")

    # Create coalition data
    coalition = df_coalitions(
        period_id,
    )
    stacked_coalition_data = make_coalition_stacked(coalition)
    unique_coalitions = stacked_coalition_data["coalition_id"].unique()

    # create line for each coalition
    for coalition_id in unique_coalitions:
        with st.container(border=True):
            cols = st.columns([1, 2, 8])
            coalition_data = stacked_coalition_data[
                stacked_coalition_data["coalition_id"] == coalition_id
            ]
            coalition_name = coalition_data["coalition_name_long"].iloc[0]
            coalition_is_government = coalition_data["coalition_in_government"].iloc[0]
            party_ids = coalition_data["party_id"].tolist()

            # government toggle
            cols[0].toggle(
                label="🏛️",
                value=coalition_is_government,
                key=f"toggle_{coalition_id}",
                on_change=create_government_coalition,
                args=(period_id, party_ids),
            )

            # coalition title
            cols[1].write(f"**{coalition_name}**")

            # coalition graph
            with cols[2]:
                GraphHorizontalStackedBar(coalition_data)


def create_government_coalition(period_id, party_ids):
    # first set all to false in period if not in party_ids
    election_results = get_entries(ElectionResult, filters={"period_id": period_id})
    for party in election_results:
        election_id = party["id"]
        party_id = party["party_id"]

        if party_id < 0:
            continue

        if party["party_id"] not in party_ids:
            update_entry(ElectionResult, election_id, {"in_government": False})
        else:
            update_entry(ElectionResult, election_id, {"in_government": True})
