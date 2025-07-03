import streamlit as st
from db import *
import pandas as pd
import plotly.graph_objects as go


class GraphElectionResult:
    def __init__(self, period_id, threshold=5):
        threshold_to_be_shown = 3
        period_year = get_entries(Period, {"id": period_id})[0]["year"]

        # Get election results
        election_results = get_entries(ElectionResult, filters={"period_id": period_id})
        if not election_results:
            st.error("No election results available for the selected period.")
            return

        percentage_non_voters = 0
        percentage_misc = 0
        # enrich dataframe with readable names
        for entry in election_results:
            party_id = entry["party_id"]
            # by not giving some entries a party_name they will not be displayed in the graph
            if party_id == -1:
                percentage_non_voters += entry["percentage"]
            if party_id == -2:
                percentage_misc += entry["percentage"]
            if party_id > 0:
                if (
                    entry["in_parliament"]
                    or entry["percentage"] >= threshold_to_be_shown
                ):
                    party = get_entries(Party, {"id": party_id})[0]
                    entry["party_name"] = party["name"]
                    entry["party_full_name"] = party["full_name"]
                    entry["color"] = party["color"]
                else:
                    percentage_misc += entry["percentage"]

        # Add miscellaneous entry if applicable
        if percentage_misc > 0:
            election_results.append(
                {
                    "party_id": -2,
                    "party_name": "Miscellaneous",
                    "party_full_name": "Miscellaneous Parties",
                    "percentage": percentage_misc,
                    "votes": 0,
                    "seats": 0,
                    "in_parliament": False,
                    "color": "#8F8F8F",  # Example color for miscellaneous parties
                }
            )

        # Create DataFrame
        dataframe = pd.DataFrame(election_results)

        # sort by percentage
        dataframe = dataframe.sort_values(by="percentage", ascending=False)

        #################################################################################
        # Create Plotly Graph with party colors
        graph = go.Figure()
        graph.add_trace(
            go.Bar(
                x=dataframe["party_full_name"],
                y=dataframe["percentage"],
                text=dataframe["percentage"].round(2).astype(str) + "%",
                textposition="outside",
                marker_color=dataframe["color"] if "color" in dataframe else None,
            )
        )
        # Extend y-axis range to give some space above the max value
        y_max = dataframe["percentage"].max()
        # Add the horizontal line as a separate shape after all traces
        graph.update_layout(
            font=dict(size=20, color="#333333"),  # Set font size and color
            xaxis=dict(tickfont=dict(size=18)),
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
            st.write(f"## Election Results {period_year}")
            st.caption("This graph shows the results of the latest election.")
            st.write(f"Voter turnout: {100 - percentage_non_voters:.2f}%")
            st.plotly_chart(graph)
