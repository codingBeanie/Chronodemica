import streamlit as st
from components.CrudTable import *
from components.Widgets import Divider
from plots.GraphPoliticalCompass import PoliticalCompass
from components.Selections import SelectionGroup
from components.DataPeriodDetails import DataManager
from plots.GraphVotingScoring import GraphVotingScoring
from properties import WIDGET_PROPERTIES
from models import *
from simulation import *


########################################################################
# Functions
def create_with_defaults(model, period_id, ref_id):
    defaults = {
        "period_id": period_id,
        f"{selections.reference.__name__.lower()}_id": ref_id,
    }
    return create_new_entry(model, defaults)


def on_change(model, id, field, key):
    value = st.session_state[
        key
    ]  # has to be read from session state here or it will be the previous value
    data = {field: value}
    update_entry(model, id, data)


#########################################################################
# Selections
st.title("Periodic Details")
st.caption("Review, Create, Edit and Delete you periodic data")
selections = SelectionGroup()

#######################################################################
# Data Manager
data_manager = DataManager(
    selections.model,
    selections.reference,
    selections.object,
    selections.period,
    selections.previous_period,
)
data = data_manager.data
complete_periodic_data = data_manager.complete_data

# Get Previous Data
if selections.previous_period:
    previous_data = data_manager.previous_data
else:
    previous_data = []

if previous_data:
    data_template_with_previous = {
        k: (selections.period["id"] if k == "period_id" else v)
        for k, v in previous_data.items()
        if k != "id"
    }
else:
    data_template_with_previous = {}

# get previous complete data
if selections.previous_period:
    previous_complete_periodic_data = data_manager.previous_complete_data
else:
    previous_complete_periodic_data = []

# Meta Statistics
total_population = data_manager.total_population
total_population_previous = data_manager.total_population_previous
nominal_change_population = data_manager.nominal_change_population
relative_change_population = data_manager.relative_change_population

#####################################################################
# Display Header
if selections.model == PartyPeriod:
    st.write(f"## {selections.object['full_name']} - {selections.period['year']}")
else:
    st.write(f"## {selections.object['name']} - {selections.period['year']}")
#####################################################################
# Creation Options when no data is available
if not data or data == []:
    st.button(
        "Create with Defaults",
        on_click=create_with_defaults,
        args=(
            selections.model,
            selections.period["id"],
            selections.object["id"],
        ),
        key="create_with_defaults",
    )
    if previous_data:
        st.button(
            "Create from Previous Period",
            on_click=create_new_entry,
            args=(selections.model, data_template_with_previous),
            key="create_from_previous",
        )

######################################################################
# General Data Display
cols = st.columns([1, 1])

# Meta Pop Data
if selections.model == PopPeriod:
    with cols[0].container(border=True):
        population = data.get("population", 0) if data else 0
        pop_ratio = population / total_population if total_population else 0
        st.write(
            f"**Total Population**: {total_population:,} ({pop_ratio:.1%} {selections.object['name']})"
        )
        st.caption(
            f"Change: {nominal_change_population:,} ({relative_change_population:.1%})"
        )

######################################################################
# INPUT_WIDGETS
if data:
    for field, properties in WIDGET_PROPERTIES.items():
        # check if the field is in the data
        if field in data:
            # create a key for the input widget
            key = f"{field}_{data['id']}"

            # create session state for the field if it doesn't exist
            if key not in st.session_state:
                st.session_state[key] = data.get(field, None)

            # get input type
            input_type = properties.get("type", None)

            # create container for the input widget
            container = cols[0].container(border=True)

            #########################################################
            # INPUTS
            # number input
            if input_type == "number":
                container.number_input(
                    properties.get("label", ""),
                    value=st.session_state[key],
                    min_value=properties.get("min", None),
                    max_value=properties.get("max", None),
                    step=properties.get("step", 1),
                    key=key,
                    on_change=on_change,
                    args=(selections.model, data["id"], field, key),
                )
            # number slider
            if input_type == "slider":
                container.slider(
                    properties.get("label", ""),
                    value=st.session_state[key],
                    min_value=properties.get("min", None),
                    max_value=properties.get("max", None),
                    step=properties.get("step", 1),
                    key=key,
                    on_change=on_change,
                    args=(selections.model, data["id"], field, key),
                )
            #########################################################
            # Change Data Display
            if previous_data:
                nominal_change = st.session_state[key] - previous_data[field]
                relative_change = (
                    (st.session_state[key] - previous_data[field])
                    / previous_data[field]
                    if previous_data[field] != 0
                    else 0
                )
                container.caption(f"Change: {nominal_change} ({relative_change:.1%})")

######################################################################
# Deletion Options
if data and data != []:
    sub_cols = cols[0].columns(5)
    with sub_cols[0]:
        st.button(
            "Reset Data",
            on_click=delete_entry,
            args=(selections.model, data["id"]),
            key="delete_all",
            type="primary",
        )

    #######################################################################
    # Graphs
    with cols[1].container():
        # Politcal Compass Graph
        with st.container(border=True):
            PoliticalCompass(
                selections.period["id"],
            )
        # Voting Scoring Graph
        if selections.model == PopPeriod:
            with st.container(border=True):
                GraphVotingScoring(data)

        # Voting Behaviour Table
        if selections.model == PopPeriod:
            voting_behavior = get_voting_behavior(data)
            dataframe_voting_behavior = pd.DataFrame(voting_behavior)
            # dump some columns
            dataframe_voting_behavior = dataframe_voting_behavior.drop(
                columns=[
                    "pop_name",
                    "pop_id",
                    "period_id",
                    "party_id",
                ]
            )
            with st.container(border=True):
                st.write("### Voting Behavior")
                st.caption(
                    "This table shows the voting behavior of the population in this period."
                )
                st.dataframe(dataframe_voting_behavior, use_container_width=True)
