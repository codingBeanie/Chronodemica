import streamlit as st
from db import *
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math


class GraphSeating:
    def __init__(self, period_id, rows=5):
        self.rows = rows
        # Get election results
        election_results = get_entries(ElectionResult, filters={"period_id": period_id})
        if not election_results:
            st.error("No election results available for the selected period.")
            return

        # Filter for parties in parliament
        parliament = [entry for entry in election_results if entry["in_parliament"]]
        if not parliament:
            st.warning("No parties in parliament for the selected period.")
            return

        # Enrich data
        for entry in parliament:
            party = get_entries(Party, {"id": entry["party_id"]})[0]
            entry["full_name"] = party["full_name"]
            entry["name"] = party["name"]
            entry["color"] = party["color"]
            entry["social_orientation"] = get_entries(
                PartyPeriod, {"party_id": entry["party_id"], "period_id": period_id}
            )[0]["social_orientation"]

        # Create DataFrame
        self.dataframe = pd.DataFrame(parliament)
        self.dataframe = self.dataframe.sort_values(by=["social_orientation"])

        # Create copy which will not be modified
        self.original_dataframe = self.dataframe.copy()

        with st.container(border=True):
            st.write("## Parliament Seating Chart")
            st.markdown(
                "🏛️ Government&nbsp;&nbsp;&nbsp;&nbsp;🧑‍🧑‍🧒‍🧒 Opposition",
                unsafe_allow_html=True,
            )
            cols = st.columns([2, 6])
            with cols[0]:
                self.show_dataframe()
            with cols[1]:
                self.draw_chart()

        ########################################################################

    def draw_chart(self):

        total_seats = sum(self.dataframe["seats"])
        cols = int(total_seats / self.rows)

        plot_data = []

        seat_count = 1
        for col in range(1, cols + 1):
            for row in range(1, self.rows + 1):
                mask = self.dataframe["seats"] > 0
                first_idx = self.dataframe[mask].index[0]
                self.dataframe.at[first_idx, "seats"] -= 1
                assigned_party = self.dataframe.loc[first_idx]
                data = {
                    "party_name": assigned_party["name"],
                    "party_full_name": assigned_party["full_name"],
                    "color": assigned_party["color"],
                    "seat_no": seat_count,
                    "row": row,
                    "col": col,
                }
                plot_data.append(data)
                seat_count += 1

        if seat_count != total_seats:
            row = 1
            col = cols + 1
            while seat_count <= total_seats:
                mask = self.dataframe["seats"] > 0
                first_idx = self.dataframe[mask].index[0]
                self.dataframe.at[first_idx, "seats"] -= 1
                assigned_party = self.dataframe.loc[first_idx]
                data = {
                    "party_name": assigned_party["name"],
                    "party_full_name": assigned_party["full_name"],
                    "color": assigned_party["color"],
                    "seat_no": seat_count,
                    "row": row,
                    "col": col,
                }
                plot_data.append(data)
                seat_count += 1
                row += 1

        plot_df = pd.DataFrame(plot_data)
        graph = go.Figure()
        graph.add_trace(
            go.Scatter(
                x=plot_df["col"],
                y=plot_df["row"],
                mode="markers",
                text=plot_df["party_full_name"],
                textposition="top center",
                marker=dict(
                    size=30,
                    color=plot_df["color"],
                    line=dict(width=0, color="DarkSlateGrey"),
                ),
            )
        )
        graph.update_layout(
            xaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
            yaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

        st.plotly_chart(graph, use_container_width=True)

    def show_dataframe(self):
        # select columns to display
        columns_to_display = [
            "name",
            "full_name",
            "seats",
            "in_government",
        ]

        # create a new DataFrame with only the selected columns
        selected_columns_df = self.original_dataframe[columns_to_display]

        # iterate over the dataframe
        for index, row in selected_columns_df.iterrows():
            with st.container(border=True):
                sm_col = st.columns([1, 1, 4, 1])
                if row["in_government"]:
                    sm_col[0].badge("Government", icon="🏛️")
                else:
                    sm_col[0].badge("Opposition", icon="🧑‍🧑‍🧒‍🧒")
                sm_col[1].write(f"**{row['name']}** ")
                sm_col[2].write(f"{row['full_name']}")
                sm_col[3].write(f"**{row['seats']}**")
