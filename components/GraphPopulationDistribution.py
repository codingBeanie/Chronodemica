import streamlit as st
from db import *
import pandas as pd
import plotly.graph_objects as go


class GraphPopulationDistribution:
    def __init__(self, period_id):
        # get all period pop data
        pop_period_data = get_entries(PopPeriod, filters={"period_id": period_id})
        if not pop_period_data:
            st.error("No population data available for the selected period.")
            return

        # Create DataFrame
        population_df = pd.DataFrame(pop_period_data).set_index("id")

        # Add population name
        for entry in population_df.iterrows():
            if "pop_id" in entry[1]:
                pop_id = entry[1]["pop_id"]
                pop_name = get_entries(Pop, filters={"id": pop_id})[0]["name"]
                population_df.at[entry[0], "pop_name"] = pop_name

        # Plotly Graph
        graph = go.Figure()
        graph.add_trace(
            go.Bar(
                x=population_df["pop_name"],
                y=population_df["population"],
                textposition="auto",
                marker_color="indianred",
            )
        )
        graph.update_layout(
            title="Population Distribution",
            xaxis_title="Population Groups",
            yaxis_title="Population Size",
            template="plotly_white",
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
