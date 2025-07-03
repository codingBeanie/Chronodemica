import streamlit as st
from db import *
from models import *


class DataManager:
    def __init__(
        self, model, reference_model, reference_object, period, previous_period
    ):
        # Input Parameters
        self.model = model
        self.reference_model = reference_model
        self.reference_id = reference_object["id"]
        self.period_id = period["id"]
        self.previous_period_id = previous_period["id"] if previous_period else None

        # Data Output Variables
        self.data = None
        self.previous_data = None
        self.complete_data = None
        self.previous_complete_data = None
        self.data_template = None
        self.total_population = None
        self.total_population_previous = None
        self.nominal_change_population = None
        self.relative_change_population = None

        #########################################################################
        # Fetch Data
        self.fetch_data()
        self.calculate_population_changes()

    def fetch_data(self):
        # Get Specific Data
        entries = get_entries(
            self.model,
            filters={
                "period_id": self.period_id,
                f"{self.reference_model.__name__.lower()}_id": self.reference_id,
            },
        )
        self.data = entries[0] if entries else None

        # Get Previous Data
        if self.previous_period_id:
            entries = get_entries(
                self.model,
                filters={
                    "period_id": self.previous_period_id,
                    f"{self.reference_model.__name__.lower()}_id": self.reference_id,
                },
            )
            self.previous_data = entries[0] if entries else None
        else:
            self.previous_data = None

        # Get Complete Data for Current Period
        self.complete_data = get_entries(
            self.model, filters={"period_id": self.period_id}
        )

        # Get Complete Data for Previous Period
        if self.previous_period_id:
            self.previous_complete_data = get_entries(
                self.model, filters={"period_id": self.previous_period_id}
            )
        else:
            self.previous_complete_data = []

    def calculate_population_changes(self):
        # Calculate Total Population for Current Period
        self.total_population = sum(
            entry.get("population", 0) for entry in self.complete_data
        )

        # Calculate Total Population for Previous Period
        if self.previous_complete_data:
            self.total_population_previous = sum(
                entry.get("population", 0) for entry in self.previous_complete_data
            )
        else:
            self.total_population_previous = 0

        # Calculate Nominal Change in Population
        self.nominal_change_population = (
            self.total_population - self.total_population_previous
        )

        # Calculate Relative Change in Population
        if self.total_population_previous != 0:
            self.relative_change_population = (
                self.nominal_change_population / self.total_population_previous
            )
        else:
            self.relative_change_population = 0.0
