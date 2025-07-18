import streamlit as st
from db import *
from models import *
from components.Widgets import Divider


class SelectionPeriod:
    def __init__(self):
        self.periods = get_entries(Period, sort_by="year", descending=True)
        self.selected_period = None
        self.previous_period = None

        if not self.periods:
            st.warning("No periods available. Please create a period first.")
            st.stop()

        self.selected_period = st.segmented_control(
            "Select Period",
            self.periods,
            format_func=lambda x: f"{x['year']}",
            key="period_selection",
        )
        if self.selected_period:
            self.previous_period = get_previous_period(self.selected_period)
        else:
            self.previous_period = None

        if not self.selected_period:
            st.warning("Please select a period to continue.")
            st.stop()


class SelectionGroup:
    def __init__(self, preselect_model=None, show_object_selection=True):
        # Output Variables
        self.model = None
        self.reference = None
        self.object = None
        self.period = None
        self.previous_period = None

        #######################################################################
        # Select Period
        periodSelection = SelectionPeriod()
        self.period = periodSelection.selected_period
        self.previous_period = periodSelection.previous_period

        # Select Data Type
        selection_items = [
            {"label": "Parties", "model": PartyPeriod, "reference": Party},
            {"label": "Population Groups", "model": PopPeriod, "reference": Pop},
        ]
        if not preselect_model:
            self.selection = st.segmented_control(
                "Select Data Type",
                selection_items,
                format_func=lambda x: x["label"],
                key="data_type_selection",
                selection_mode="single",
            )
        else:
            self.selection = next(
                item for item in selection_items if item["model"] == preselect_model
            )

        if not self.selection:
            st.warning("Please select a data type to manage.")
            st.stop()

        self.model = self.selection["model"]
        self.reference = self.selection["reference"]

        #######################################################################
        # Select Object of Data Type
        if show_object_selection:
            model_objects = get_entries(
                self.reference, sort_by="name", descending=False
            )
            if not model_objects:
                st.warning(
                    f"No {self.reference.__name__.lower()}s available. Please create one first."
                )
                st.stop()

            self.object = st.segmented_control(
                f"Select {self.reference.__name__}",
                model_objects,
                format_func=lambda x: x["name"],
                key="ref_selection",
            )
        ########################################################################
        # Check if a selection was made
        Divider(title="")
        if not self.period:
            st.warning("Please select a period view data.")
            st.stop()
        if not self.object and show_object_selection:
            st.warning(
                f"Please select a {self.reference.__name__.lower()} to continue."
            )
            st.stop()
