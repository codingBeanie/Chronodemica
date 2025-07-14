import streamlit as st
from db import *
from models import *
import plotly.graph_objects as go
from dataframes import *


def graph_stacked_bar_h(
    dataframe, x_column, y_column, text_column, color_column, title
):
    x_title = x_column.replace("_", " ").title()
    graph = go.Figure()
    # Get unique parties
    for entry in dataframe[f"{y_column}"].unique():
        sub_dataframe = dataframe[dataframe[f"{y_column}"] == entry]
        graph.add_trace(
            go.Bar(
                y=sub_dataframe[f"{y_column}"],
                x=sub_dataframe[f"{x_column}"],
                orientation="h",
                marker_color=sub_dataframe[f"{color_column}"],
                text=sub_dataframe[f"{text_column}"],
                hoverinfo="text + x",
            )
        )
    graph.update_layout(
        barmode="stack",
        showlegend=False,
        margin=dict(l=0, r=0, t=80, b=0),
        title=dict(text=title, font=dict(size=24), x=0.5, xanchor="center"),
        yaxis=dict(
            tickfont=dict(size=18),
        ),
        xaxis=dict(
            title=dict(text=f"{x_title}", font=dict(size=14)),
            tickfont=dict(size=12),
            showgrid=True,
            gridwidth=1,
            gridcolor="LightGray",
        ),
    )

    graph.update_traces(
        textfont_size=14, textposition="inside", insidetextanchor="middle"
    )

    st.plotly_chart(graph, use_container_width=True)
