from models import *
from db import *
import streamlit as st
import pandas as pd
import itertools
from simulation import calculate_distance


def df_election_results(period_id, misc_threshold=0):
    election_results = get_entries(
        ElectionResult,
        filters={"period_id": period_id},
    )
    dataframe = pd.DataFrame(election_results)
    # enrich dataframe with readable names
    dataframe = enrich_df_party_data(dataframe)
    dataframe = enrich_df_period_data(dataframe)
    dataframe = enrich_df_previous_data(
        dataframe=dataframe,
        model=ElectionResult,
        searchColumns=["party_id"],
        period_id=period_id,
        valueColumns=["votes"],
    )
    dataframe = enrich_df_percentages(dataframe, "votes")
    dataframe = enrich_df_percentages(dataframe, "previous_votes")
    dataframe = enrich_df_change_percentage(dataframe)
    dataframe = move_small_values_to_misc(dataframe, misc_threshold)

    # sorting the dataframe
    dataframe = dataframe.sort_values(
        by=["votes", "party_name"], ascending=[False, True]
    )
    dataframe = sort_misc_to_end(dataframe)

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
    dataframe = enrich_df_previous_data(
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
    dataframe = enrich_df_previous_data(
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


def df_coalitions(period_id):

    # Get Election Results
    election_results = get_entries(ElectionResult, {"period_id": period_id})
    # filter in_parliament
    parliament = [
        result for result in election_results if result["in_parliament"] is True
    ]

    dataframe = pd.DataFrame(parliament)

    # Enrich data
    dataframe = enrich_df_party_data(dataframe)
    dataframe["period_id"] = period_id

    # sort by most seats
    dataframe = dataframe.sort_values(by="seats", ascending=False)

    # Sum of seats
    total_seats = sum(entry["seats"] for entry in dataframe.to_dict("records"))
    majority_seats = int(total_seats / 2) + 1

    # Create Coalitions
    coalition_mapping = []
    party_combinations = []

    # Create all combinations of parties in parliament
    for r in range(2, len(dataframe) + 1):
        party_combinations.extend(
            itertools.combinations(dataframe.to_dict("records"), r)
        )

    # Iterate through each combination and calculate coalition values
    for combination in party_combinations:
        total_seats_combination = sum(party["seats"] for party in combination)
        has_majority = total_seats_combination > majority_seats
        party_ids = [party["party_id"] for party in combination]
        combination_id = "-".join(str(party_id) for party_id in sorted(party_ids))
        party_names = [party["party_name"] for party in combination]
        party_fullnames = [party["party_full_name"] for party in combination]
        party_seats = [party["seats"] for party in combination]
        parties_in_government = [party["in_government"] for party in combination]

        if has_majority:
            coalition_mapping.append(
                {
                    "combination_id": combination_id,
                    "period_id": period_id,
                    "total_seats_in_parliament": total_seats,
                    "majority_seats": majority_seats,
                    "party_ids": party_ids,
                    "no_of_parties": len(party_ids),
                    "party_names": party_names,
                    "party_fullnames": party_fullnames,
                    "party_seats": party_seats,
                    "parties_in_government": parties_in_government,
                    "total_seats": total_seats_combination,
                }
            )

    # Filter out supersets
    filtered_coalitions = []
    for coalition in coalition_mapping:
        is_superset = False
        for other_coalition in coalition_mapping:
            if coalition["combination_id"] != other_coalition["combination_id"] and set(
                coalition["party_ids"]
            ).issuperset(other_coalition["party_ids"]):
                is_superset = True
                break
        if not is_superset:
            filtered_coalitions.append(coalition)

    # sort coalitions by number of parties and total seats
    filtered_coalitions = sorted(
        filtered_coalitions,
        key=lambda x: (-x["no_of_parties"], x["total_seats"]),
        reverse=True,
    )
    return pd.DataFrame(filtered_coalitions)


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


def enrich_df_previous_data(
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


def make_coalition_stacked(dataframe):
    stacked_data = []
    total_seats = dataframe["total_seats_in_parliament"].iloc[0]
    majority_seats = dataframe["majority_seats"].iloc[0]

    for index, coalition in dataframe.iterrows():
        coalition_id = coalition["combination_id"]
        # parties and seats will be combined and sorted by seats
        party_seats_list = sorted(
            zip(
                coalition["party_fullnames"],
                coalition["party_names"],
                coalition["party_ids"],
                coalition["party_seats"],
            ),
            key=lambda x: x[3],
            reverse=True,
        )
        # zipped data will be turn back into separate lists
        parties_fullname_list, parties_list, party_ids_list, seats_list = zip(
            *party_seats_list
        )
        parties_fullname_list = list(parties_fullname_list)
        parties_list = list(parties_list)
        party_ids_list = list(party_ids_list)
        seats_list = list(seats_list)

        coalition_name_long = " / ".join(parties_fullname_list)
        coalition_name_short = " / ".join(parties_list)
        coalition_in_government = all(coalition["parties_in_government"])

        # iterate through each party in coalition and add to stacked data
        for index, party in enumerate(parties_list):
            party_name = party
            party_fullname = parties_fullname_list[index]
            party_id = party_ids_list[index]
            party_seats = seats_list[index]

            # get party object for getting the color
            party_object = get_entries(Party, {"id": party_id})
            party_color = party_object[0]["color"] if party_object else "#FFFFFF"

            # add to stacked data
            stacked_data.append(
                {
                    "coalition_id": coalition_id,
                    "period_id": coalition["period_id"],
                    "coalition_name_long": coalition_name_long,
                    "coalition_name_short": coalition_name_short,
                    "party_name": party_fullname,
                    "party_full_name": party_name,
                    "party_id": party_id,
                    "party_color": party_color,
                    "party_seats": party_seats,
                    "coalition_in_government": coalition_in_government,
                    "total_seats_in_parliament": total_seats,
                    "majority_seats": majority_seats,
                }
            )

        stacked_dataframe = pd.DataFrame(stacked_data)
    return stacked_dataframe


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


def sort_misc_to_end(dataframe):
    # Select the row(s) to move
    misc_row = dataframe[dataframe["party_id"] == -2]
    # Drop them from the original DataFrame
    dataframe = dataframe[dataframe["party_id"] != -2]
    # Append at the end (ignore_index keeps the index clean)
    dataframe = pd.concat([dataframe, misc_row], ignore_index=True)
    return dataframe


def move_small_values_to_misc(dataframe, threshold=3.0):
    # if misc_threshold is set, filter out parties below the threshold and add them to Miscellaneous
    if threshold > 0:
        for index, entry in dataframe.iterrows():
            if entry["votes_percentage"] < threshold and entry["party_id"] > 0:
                # add to Miscellaneous
                dataframe.loc[dataframe["party_id"] == -2, "votes"] += entry["votes"]
                dataframe.loc[dataframe["party_id"] == -2, "previous_votes"] += entry[
                    "previous_votes"
                ]
                dataframe.loc[dataframe["party_id"] == -2, "votes_percentage"] += entry[
                    "votes_percentage"
                ]
                dataframe.loc[
                    dataframe["party_id"] == -2, "previous_votes_percentage"
                ] += entry["previous_votes_percentage"]

                # remove from dataframe
                dataframe = dataframe.drop(index)
    return dataframe
