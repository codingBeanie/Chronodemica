import streamlit as st
from db import *
from models import *
import plotly.graph_objects as go


class GraphElection:
    def __init__(self, dataframe, title, threshold=0):
        period_year = dataframe["period_year"].iloc[0]
        percentage_non_voters = dataframe[dataframe["party_id"] == -1][
            "votes_percentage"
        ].sum()
        dataframe = dataframe[
            (dataframe["party_id"] > 0) | (dataframe["party_id"] == -2)
        ].copy()

        graph = go.Figure()
        graph.add_trace(
            go.Bar(
                x=dataframe["party_full_name"],
                y=dataframe["votes_percentage"],
                marker_color=dataframe["party_color"],
                text=dataframe["votes_percentage"].round(2).astype(str) + "%",
                textposition="none",  # We'll use texttemplate instead
            )
        )
        # Extend y-axis range to give some space above the max value
        y_max = dataframe["votes_percentage"].max()
        # Add the horizontal line as a separate shape after all traces
        graph.update_layout(
            font=dict(size=20, color="#333333"),  # Set font size and color
            xaxis=dict(
                tickfont=dict(size=18),
                tickmode="array",
                tickvals=list(range(len(dataframe))),
                ticktext=[
                    f"{name}<br><b>{perc:.1f}%</b><br><i>({change})</i>"
                    for perc, name, change in zip(
                        dataframe["votes_percentage"],
                        dataframe["party_full_name"],
                        dataframe["change_percentage"],
                    )
                ],
            ),
            yaxis=dict(
                tickfont=dict(size=18),
                range=[0, y_max * 1.1],  # 10% more than max value
                showgrid=True,
                gridcolor="#CCCCCC",  # Stronger grid line color
            ),
            margin=dict(l=10, r=10, t=10, b=10),  # Reduce all margins
        )
        # Add the horizontal line shape after layout so it appears below traces
        graph.add_shape(
            type="line",
            xref="paper",
            x0=0,
            x1=1,
            yref="y",
            y0=threshold,
            y1=threshold,
            line=dict(
                color="#333333",  # Choose a strong color
                width=2,  # Make the line thicker
                dash="solid",  # Solid line
            ),
            layer="below",
        )

        with st.container(border=True):
            st.write(f"## {title}")
            st.caption("This graph shows the results of an election.")
            st.write(f"Voter turnout: {100 - percentage_non_voters:.2f}%")
            st.plotly_chart(graph)
