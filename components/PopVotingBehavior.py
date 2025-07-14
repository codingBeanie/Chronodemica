import streamlit as st
from plots.GraphStackedBarH import graph_stacked_bar_h
from dataframes import *


def pop_voting_behavior(period_id):
    pop_votes = df_pop_votes(period_id)

    with st.container(border=True):
        graph_stacked_bar_h(
            pop_votes,
            x_column="votes",
            y_column="pop_name",
            color_column="party_color",
            text_column="party_name",
            title=f"Population Group Voting (Total Votes)",
        )
    with st.container(border=True):
        graph_stacked_bar_h(
            pop_votes,
            x_column="votes_pop_name_percentage",
            y_column="pop_name",
            color_column="party_color",
            text_column="party_name",
            title=f"Population Group Voting (Relative Votes)",
        )
