import streamlit as st
from db import *
import pandas as pd


class CrudTable:
    def __init__(self, model):
        self.model = model  # will be needed to address the models crud methods
        self.key = f"{self.model.__name__}_crud_table"  # is needed to get the changed data from the session state

        # i want changes to be processed only after submitting, but need to show an indicator beforehand
        if f"{self.key}_unsaved" not in st.session_state:
            st.session_state[f"{self.key}_unsaved"] = False

        # get data from db
        self.data = get_entries(self.model)
        self.dataframe = pd.DataFrame(self.data).set_index("id")

        # create table
        self.table = st.data_editor(
            self.dataframe,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key=self.key,
            on_change=self.on_change,
            column_config={"id": st.column_config.Column("ID", disabled=True)},
        )

        # create submit button
        cols = st.columns([7, 1])
        if st.session_state[f"{self.key}_unsaved"]:
            cols[0].warning(
                "You have unsaved changes. Please submit them before leaving this page."
            )
        cols[1].button(
            "Submit", on_click=self.submit, type="primary", key=f"{self.key}_submit"
        )

    def on_change(self):
        st.session_state[f"{self.key}_unsaved"] = True

    def submit(self):
        st.session_state[f"{self.key}_unsaved"] = False

        # any changes are stored in the session state
        added_data = st.session_state[self.key].get("added_rows", [])
        edited_data = st.session_state[self.key].get("edited_rows", [])
        deleted_data = st.session_state[self.key].get("deleted_rows", [])

        # add new entries
        for row in added_data:
            create_new_entry(self.model, row)

        # edit existing entries
        for row in edited_data.items():
            row_id, row_data = row
            entry_id = self.dataframe.index[int(row_id)]
            update_entry(self.model, entry_id, row_data)

        # delete entries
        for row in deleted_data:
            entry_id = self.dataframe.index[int(row)]
            delete_entry(self.model, entry_id)
