from models import *
from db import *
import streamlit as st
import pandas as pd


def df_election_results(period_id):
    election_results = get_entries(
        ElectionResult,
        filters={"period_id": period_id},
    )
    dataframe = pd.DataFrame(election_results)
    # enrich dataframe with readable names
    dataframe = enrich_df_party_data(dataframe)
    dataframe = enrich_df_period_data(dataframe)
    dataframe = df_enrich_previous_data(
        dataframe=dataframe,
        model=ElectionResult,
        searchColumns=["party_id"],
        period_id=period_id,
        valueColumns=["votes"],
    )
    dataframe = enrich_df_percentages(dataframe, "votes")
    dataframe = enrich_df_percentages(dataframe, "previous_votes")
    dataframe = enrich_df_change_percentage(dataframe)

    dataframe = dataframe.sort_values(
        by=["votes", "party_name"], ascending=[False, True]
    )
    return dataframe


def df_pop_votes(period_id, pop_id):
    pop_votes = get_entries(
        PopVote,
        filters={"period_id": period_id, "pop_id": pop_id},
    )
    dataframe = pd.DataFrame(pop_votes)

    # enrich dataframe with readable names
    dataframe = enrich_df_pop_data(dataframe)
    dataframe = enrich_df_party_data(dataframe)
    dataframe = enrich_df_period_data(dataframe)
    dataframe = df_enrich_previous_data(
        dataframe=dataframe,
        model=PopVote,
        searchColumns=["party_id", "pop_id"],
        period_id=period_id,
        valueColumns=["votes"],
    )
    dataframe = enrich_df_percentages(dataframe, "votes")
    dataframe = enrich_df_percentages(dataframe, "previous_votes")
    dataframe = enrich_df_change_percentage(dataframe)

    dataframe = dataframe.sort_values(
        by=["votes", "party_name"], ascending=[False, True]
    )
    dataframe = dataframe.sort_values(
        by=["votes", "party_name"], ascending=[False, True]
    )
    return dataframe


def df_party_votes(period_id, party_id):
    # get all pops in period
    pop_votes = get_entries(
        PopVote,
        filters={"period_id": period_id, "party_id": party_id},
    )
    dataframe = pd.DataFrame(pop_votes)
    # enrich dataframe with readable names
    dataframe = enrich_df_pop_data(dataframe)
    dataframe = enrich_df_party_data(dataframe)
    dataframe = enrich_df_period_data(dataframe)
    dataframe = df_enrich_previous_data(
        dataframe=dataframe,
        model=PopVote,
        searchColumns=["party_id", "pop_id"],
        period_id=period_id,
        valueColumns=["votes"],
    )
    dataframe = enrich_df_percentages(dataframe, "votes")
    dataframe = enrich_df_percentages(dataframe, "previous_votes")
    dataframe = enrich_df_change_percentage(dataframe)

    # renaming columns for compatibility with GraphElection
    dataframe = dataframe.rename(
        columns={
            "party_name": "party_name_reserve",
            "party_full_name": "party_full_name_reserve",
            "pop_name": "party_full_name",
        }
    )
    dataframe = dataframe.sort_values(by=["votes"], ascending=[False])
    return dataframe


#############################################################################################


def enrich_df_party_data(dataframe):
    for index, entry in dataframe.iterrows():
        party_id = int(entry["party_id"])
        if party_id > 0:
            party = get_entries(Party, {"id": party_id})[0]
            dataframe.at[index, "party_name"] = party["name"]
            dataframe.at[index, "party_full_name"] = party["full_name"]
            dataframe.at[index, "party_color"] = party["color"]
        if party_id == -1:
            dataframe.at[index, "party_name"] = "Non Voters"
            dataframe.at[index, "party_full_name"] = "Non Voters"
            dataframe.at[index, "party_color"] = "#FFAFAF"
        if party_id == -2:
            dataframe.at[index, "party_name"] = "Miscellaneous"
            dataframe.at[index, "party_full_name"] = "Miscellaneous Parties"
            dataframe.at[index, "party_color"] = "#8F8F8F"
    return dataframe


def enrich_df_pop_data(dataframe):
    for index, entry in dataframe.iterrows():
        pop_id = int(entry["pop_id"])
        pop = get_entries(Pop, {"id": pop_id})[0]
        dataframe.at[index, "pop_name"] = pop["name"]
    return dataframe


def enrich_df_period_data(dataframe):
    for index, entry in dataframe.iterrows():
        # enrich current period
        period_id = int(entry["period_id"])
        period = get_entries(Period, {"id": period_id})[0]
        dataframe.at[index, "period_year"] = str(period["year"])

    return dataframe


def enrich_df_percentages(dataframe, column):
    if column not in dataframe.columns:
        return dataframe
    # Calculate the percentage of the specified column
    total = dataframe[column].sum()
    if total > 0:
        dataframe[f"{column}_percentage"] = (dataframe[column] / total * 100).round(2)
    else:
        dataframe[f"{column}_percentage"] = None

    return dataframe


def df_enrich_previous_data(
    dataframe=None, model=None, searchColumns=None, period_id=None, valueColumns=None
):
    previous_period = get_previous_periods(period_id)
    # There is no previous period
    if not previous_period:
        for valueColumn in valueColumns:
            # Add a column for previous values with None
            dataframe[f"previous_{valueColumn}"] = None
        return dataframe

    # iterate through the dataframe and add previous data
    for index, entry in dataframe.iterrows():
        # Find the previous data entry that matches the current search criteria
        search_criteria = {
            "period_id": previous_period["id"],
        }
        for searchColumn in searchColumns:
            search_criteria[searchColumn] = entry[searchColumn]
        previous_entry = get_entries(model, filters=search_criteria)[0]

        if previous_entry:
            for valueColumn in valueColumns:
                # Add the previous data to the current dataframe
                previous_value = previous_entry.get(valueColumn, None)
                dataframe.at[index, f"previous_{valueColumn}"] = previous_value

    return dataframe


def enrich_df_change_percentage(dataframe):
    if not dataframe["previous_votes"].isnull().all():
        dataframe["change_percentage"] = (
            (dataframe["votes_percentage"] - dataframe["previous_votes_percentage"])
        ).round(2)
    else:
        dataframe["change_percentage"] = None

    return dataframe


#####################################################################################################
def get_previous_periods(period_id):
    period_id = int(period_id)
    periods = get_entries(Period)
    periods = sorted(periods, key=lambda x: x["year"], reverse=False)

    # find current period
    current_period_index = next(
        (i for i, p in enumerate(periods) if p["id"] == period_id), None
    )
    if current_period_index > 0:
        # finde the previous period
        previous_period_index = current_period_index - 1
        previous_period = periods[previous_period_index]
        return previous_period

    return []
