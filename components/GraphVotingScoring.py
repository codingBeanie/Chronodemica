import streamlit as st
from db import *
import pandas as pd
import plotly.graph_objects as go
from simulation import *
import numpy as np


class GraphVotingScoring:
    def __init__(self, pop_period):
        self.pop_period = pop_period

        self.get_basic_line()
        self.get_point_data()
        self.get_party_data()
        st.write("### Voting Scoring Graph")
        st.caption("This graph shows the voting score based on political distance. ")
        self.render()

    ##########################################################################################
    def get_basic_line(self):
        # Basic line
        x_values = list(range(0, 101, 1))
        y_values = []
        for x in x_values:
            y_values.append(calculate_score(self.pop_period, x))

        # Create DataFrame
        self.basic_data = pd.DataFrame({"x": x_values, "y": y_values})

    ##########################################################################################
    def get_point_data(self):
        # Non-voter point
        self.non_voters_distance = self.pop_period["non_voters_distance"]
        self.non_voter_score = calculate_score(
            self.pop_period, self.non_voters_distance
        )
        self.non_voter_data = pd.DataFrame(
            {
                "x": [self.non_voters_distance],
                "y": [self.non_voter_score],
            }
        )
        # Small-party voter point
        self.small_party_distance = self.pop_period["small_party_distance"]
        self.small_party_score = calculate_score(
            self.pop_period, self.small_party_distance
        )
        self.small_party_data = pd.DataFrame(
            {
                "x": [self.small_party_distance],
                "y": [self.small_party_score],
            }
        )

    ############################################################################################
    def get_party_data(self):
        # Get party data for the current period
        party_periods = get_entries(
            PartyPeriod, {"period_id": self.pop_period["period_id"]}
        )
        self.party_data = []
        for party_period in party_periods:
            party = get_entries(Party, {"id": party_period["party_id"]})[0]
            distance = get_distance(self.pop_period, party_period)
            score = calculate_score(self.pop_period, distance)
            self.party_data.append(
                {
                    "name": party["name"],
                    "full_name": party["full_name"],
                    "distance": distance,
                    "score": score,
                    "color": party["color"],
                }
            )

    ##########################################################################################
    def render(self):
        graph = go.Figure()
        # Basic line
        graph.add_trace(
            go.Scatter(
                x=self.basic_data["x"],
                y=self.basic_data["y"],
                mode="lines",
                name="Voting Score",
                line=dict(color="#333333", width=2),
            )
        )
        # Non-voter point
        graph.add_trace(
            go.Scatter(
                x=self.non_voter_data["x"],
                y=self.non_voter_data["y"],
                mode="markers+text",
                name="Non-Voter",
                marker=dict(size=10),
                text="Non-Voter",
                textposition="top center",
            )
        )
        # Small-party voter point
        graph.add_trace(
            go.Scatter(
                x=self.small_party_data["x"],
                y=self.small_party_data["y"],
                mode="markers+text",
                name="Small-Party Voter",
                marker=dict(size=10),
                text="Small-Party Voter",
                textposition="top center",
            )
        )
        # Party data points
        for party in self.party_data:
            graph.add_trace(
                go.Scatter(
                    x=[party["distance"]],
                    y=[party["score"]],
                    mode="markers+text",
                    name=party["name"],
                    marker=dict(
                        size=30, color=party.get("color", "#333333"), opacity=1.0
                    ),
                    text=party["full_name"] or party["name"],
                    textposition="top center",
                )
            )

        graph.update_layout(
            xaxis_title="Political Distance (%)",
            yaxis_title="Voting Score (%)",
            template="plotly_white",
            margin=dict(l=10, r=10, t=0, b=10),
            font=dict(family="sans-serif", size=16, color="#333333"),
            showlegend=False,
            xaxis=dict(
                tickmode="array",
                tickvals=np.arange(0, 101, 10),
                range=[0, 100],
            ),
            yaxis=dict(
                tickmode="array",
                tickvals=np.arange(0, 101, 10),
                range=[0, 105],
            ),
        )
        graph.update_traces(
            marker_line_color="black", marker_line_width=1.5, opacity=0.6
        )
        graph.update_yaxes(tickformat="d")
        graph.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=500,
            width=800,
        )
        # Display the graph
        st.plotly_chart(graph, use_container_width=True)
