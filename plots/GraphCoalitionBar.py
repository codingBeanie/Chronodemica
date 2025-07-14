import streamlit as st
from db import *
from models import *
import plotly.graph_objects as go
from dataframes import *


def GraphCoalitionBar(dataframe):
    graph = go.Figure()
    # Get unique parties
    for party in dataframe["party_name"].unique():
        df_party = dataframe[dataframe["party_name"] == party]
        graph.add_trace(
            go.Bar(
                y=df_party["coalition_name_short"],  # y = coalitions
                x=df_party["party_seats"],  # x = seats
                name=df_party["party_full_name"].iloc[0],  # name = party name
                marker_color=df_party["party_color"].iloc[0],
                orientation="h",
                text=df_party["party_seats"],
            )
        )
    # Add vertical line at majority_seats
    graph.add_shape(
        type="line",
        x0=dataframe["majority_seats"].iloc[0],
        x1=dataframe["majority_seats"].iloc[0],
        y0=-0.5,
        y1=0.5,
        line=dict(color="red", width=1, dash="dash"),
        xref="x",
        yref="y",
    )
    graph.update_layout(
        barmode="stack",
        showlegend=False,
        margin=dict(l=120, r=0, t=0, b=0),
        height=50,
        title=None,
        yaxis=dict(
            showticklabels=False,
        ),
        xaxis=dict(
            range=[
                0,
                dataframe["total_seats_in_parliament"].iloc[0],
            ],
            showticklabels=False,
        ),
    )
    graph.update_traces(
        textfont_size=16, textposition="inside", insidetextanchor="middle"
    )
    st.plotly_chart(graph, use_container_width=True)
