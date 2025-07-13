import streamlit as st
from db import *
import pandas as pd
import plotly.graph_objects as go


class PoliticalCompass:
    def __init__(self, period_id):
        #######################################################################
        # Get PopPeriod Data for total population
        pop_period_data = get_entries(PopPeriod, filters={"period_id": period_id})
        if not pop_period_data:
            st.error("No population data available for the selected period.")
            return
        total_population = sum(
            entry["population"] for entry in pop_period_data if "population" in entry
        )
        # Get Population Data
        population_data = get_entries(PopPeriod, filters={"period_id": period_id})
        population_df = pd.DataFrame(population_data).set_index("id")
        for entry in population_df.iterrows():
            if "pop_id" in entry[1]:
                pop_id = entry[1]["pop_id"]
                pop_name = get_entries(Pop, filters={"id": pop_id})[0]["name"]
                population_df.at[entry[0], "pop_name"] = pop_name
                pop_size = get_entries(
                    PopPeriod, filters={"period_id": period_id, "pop_id": pop_id}
                )[0]["population"]
                population_df.at[entry[0], "pop_size"] = pop_size
                population_df.at[entry[0], "pop_size_ratio"] = (
                    pop_size / total_population
                ) * 300

        # st.write(population_df)

        # get party data
        party_data = get_entries(
            PartyPeriod,
            filters={"period_id": period_id},
        )
        if not party_data:
            st.error("No party data available for the selected period.")
            return
        party_df = pd.DataFrame(party_data).set_index("id")
        for entry in party_df.iterrows():
            if "party_id" in entry[1]:
                party_id = entry[1]["party_id"]
                party = get_entries(Party, filters={"id": party_id})[0]
                party_name = party["name"]
                party_full_name = party["full_name"]
                party_color = party["color"]

                party_df.at[entry[0], "party_name"] = party_name
                party_df.at[entry[0], "party_full_name"] = party_full_name
                party_df.at[entry[0], "color"] = party_color

        # st.write(party_df)

        ####################################################################
        # Create Plotly Graph
        graph = go.Figure()

        # Population-Scatter
        graph.add_trace(
            go.Scatter(
                x=population_df["social_orientation"],
                y=population_df["economic_orientation"],
                mode="markers+text",
                marker=dict(
                    size=population_df["pop_size_ratio"],
                    color="#333333",
                    opacity=0.8,
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
                name="Population",
                text=population_df["pop_name"],
                textposition="top center",
                hovertext=population_df["pop_size"],
                hoverinfo="text",
                textfont=dict(
                    size=18,
                    color="#333333",
                ),
            )
        )

        # Party-Scatter
        graph.add_trace(
            go.Scatter(
                x=party_df["social_orientation"],
                y=party_df["economic_orientation"],
                mode="markers+text",
                marker=dict(
                    size=party_df["political_strength"],
                    color=party_df["color"],
                ),
                name="Party",
                text=party_df["party_name"],
                textposition="top center",
                hovertext=party_df["party_full_name"],
                hoverinfo="text",
                textfont=dict(
                    size=18,
                    color="#333333",
                ),
            )
        )

        graph.update_layout(
            legend_title="Group",
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(
                family="sans-serif",  # or "Arial", "Helvetica", etc.)
            ),
            xaxis=dict(
                range=[-130, 130],
                showticklabels=False,  # Hide x-axis ticks
                ticks="",  # Hide x-axis tick marks
            ),
            yaxis=dict(
                range=[-130, 130],
                showticklabels=False,  # Hide y-axis ticks
                ticks="",  # Hide y-axis tick marks
            ),
            showlegend=False,
            width=600,  # Set width
            height=600,  # Set height (same as width for square)
            shapes=[
                # Vertical line at x=0
                dict(
                    type="line",
                    x0=0,
                    x1=0,
                    y0=-120,
                    y1=120,
                    line=dict(color="#333333", width=1),
                ),
                # Horizontal line at y=0
                dict(
                    type="line",
                    x0=-120,
                    x1=120,
                    y0=0,
                    y1=0,
                    line=dict(color="#333333", width=1),
                ),
            ],
            annotations=[
                dict(
                    x=-130,
                    y=130,
                    text="Authoritarian Socialism",
                    showarrow=False,
                    font=dict(size=14, color="#8E1616"),
                    xanchor="left",
                    yanchor="top",
                ),
                dict(
                    x=130,
                    y=130,
                    text="Corporatist Nationalism",
                    showarrow=False,
                    font=dict(size=14, color="#8E1616"),
                    xanchor="right",
                    yanchor="top",
                ),
                dict(
                    x=-130,
                    y=-130,
                    text="Anarcho-Communism",
                    showarrow=False,
                    font=dict(size=14, color="#8E1616"),
                    xanchor="left",
                    yanchor="bottom",
                ),
                dict(
                    x=130,
                    y=-130,
                    text="Anarcho-Capitalism",
                    showarrow=False,
                    font=dict(size=14, color="#8E1616"),
                    xanchor="right",
                    yanchor="bottom",
                ),
                dict(
                    x=10,
                    y=-130,
                    text="Liberalism",
                    showarrow=False,
                    font=dict(size=12, color="#F8EEDF"),
                    xanchor="right",
                    yanchor="bottom",
                    bgcolor="#333333",
                    bordercolor="black",
                    borderwidth=1,
                ),
                dict(
                    x=13,
                    y=120,
                    text="Authoritarian",
                    showarrow=False,
                    font=dict(size=12, color="#F8EEDF"),
                    xanchor="right",
                    yanchor="bottom",
                    bgcolor="#333333",
                    bordercolor="black",
                    borderwidth=1,
                ),
                dict(
                    x=-130,
                    y=5,
                    text="Communalism",
                    showarrow=False,
                    font=dict(size=12, color="#F8EEDF"),
                    xanchor="left",
                    yanchor="top",
                    bgcolor="#333333",
                    bordercolor="black",
                    borderwidth=1,
                ),
                dict(
                    x=100,
                    y=5,
                    text="Individualism",
                    showarrow=False,
                    font=dict(size=12, color="#F8EEDF"),
                    xanchor="left",
                    yanchor="top",
                    bgcolor="#333333",
                    bordercolor="black",
                    borderwidth=1,
                ),
            ],
        )
        st.write("## Political Compass")
        st.caption(
            "Compass graph showing the social and economic orientations of the population groups and parties in the selected period. The size of the markers for the parties represents the political strength, the markers of the population groups the size."
        )
        st.plotly_chart(graph, use_container_width=True)
