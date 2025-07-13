from models import *
from db import *
import numpy as np
import streamlit as st


def get_distance(pop_period, party_period):
    pop_social = pop_period["social_orientation"]
    pop_economic = pop_period["economic_orientation"]
    party_social = party_period["social_orientation"]
    party_economic = party_period["economic_orientation"]
    # calculate distance
    distance_ratio = calculate_distance(
        pop_social, pop_economic, party_social, party_economic, ratio=True
    )
    return distance_ratio


def calculate_distance(social_1, economic_1, social2, economic2, ratio=True):
    # calculate distance
    distance = np.sqrt((social_1 - social2) ** 2 + (economic_1 - economic2) ** 2)
    if not ratio:
        return distance

    # normalize distance to a percentage (0-100)
    distance_ratio = int((distance / 282.8427 if distance != 0 else 0) * 100)
    return distance_ratio


def calculate_score(pop_period, distance):
    # extract parameters
    max_distance = pop_period["max_political_distance"]
    variety = pop_period["variety_tolerance"] / 2
    falloff = 0.2

    # max distance cap
    if distance > max_distance:
        return 0

    # calculate
    # Gauß-function
    score = np.exp(-(distance**2) / (2 * variety**2))

    # logistic function
    # score = 1 / (1 + np.exp(falloff * (distance - variety)))

    # exponential decay function
    # score = (1 - distance / 100) ** falloff

    # round to integer
    rounded_score = int(np.round(score * 100))

    return rounded_score


def calculate_adjusted_score(party_period, score):
    # extract parameters
    strength = party_period["political_strength"]
    # New Method: Linear function with negative score adjustment below 50
    strenght_modifier = np.interp(strength, [0, 100], [0.05, 1.5])
    adjusted_score = int(score * strenght_modifier)

    # Old Method of just creating a stronger score
    # adjusted_score = int(score * (1 + (strength / 100)))
    return adjusted_score


def get_voting_behavior(pop_period):

    # extract parameters
    pop_id = pop_period["pop_id"]
    period_id = pop_period["period_id"]

    # get reference models
    pop = get_entries(Pop, {"id": pop_id})[0]
    period = get_entries(Period, {"id": period_id})[0]
    party_period = get_entries(PartyPeriod, {"period_id": period_id})

    # get additional data
    pop_name = pop["name"]
    period_year = period["year"]
    pop_population = pop_period["population"]
    ratio_eligible = pop_period["ratio_eligible"]
    eligible_population = int((pop_population * ratio_eligible) / 100)

    # create return data structure
    voting_behavior = []
    for entry in party_period:
        # get reference data
        party_id = entry["party_id"]
        party = get_entries(Party, {"id": party_id})[0]

        distance = get_distance(pop_period, entry)
        raw_score = calculate_score(pop_period, distance)
        adjusted_score = calculate_adjusted_score(entry, raw_score)

        # create line data
        line_data = {
            "pop_id": pop_id,
            "pop_name": pop_name,
            "period_id": period_id,
            "party_id": party_id,
            "party_name": party["name"],
            "party_full_name": party["full_name"],
            "distance": distance,
            "raw_score": raw_score,
            "strength": entry["political_strength"],
            "adjusted_score": adjusted_score,
        }
        voting_behavior.append(line_data)

    # add non-voter and small-party data
    non_voters_distance = pop_period["non_voters_distance"]
    non_voter_score = calculate_score(pop_period, non_voters_distance)
    voting_behavior.append(
        {
            "pop_id": pop_id,
            "pop_name": pop_name,
            "period_id": period_id,
            "party_id": -1,  # Non-voters have no party ID
            "party_name": "Non-Voters",
            "party_full_name": "Non-Voters",
            "distance": non_voters_distance,
            "raw_score": non_voter_score,
            "strength": 0,  # Non-voters have no political strength
            "adjusted_score": non_voter_score,  # Non-voters score is not adjusted
        }
    )
    small_party_distance = pop_period["small_party_distance"]
    small_party_score = calculate_score(pop_period, small_party_distance)
    voting_behavior.append(
        {
            "pop_id": pop_id,
            "pop_name": pop_name,
            "period_id": period_id,
            "party_id": -2,  # Small parties have no party ID
            "party_name": "Small Parties",
            "party_full_name": "Small Parties",
            "distance": small_party_distance,
            "raw_score": small_party_score,
            "strength": 0,  # Small parties have no political strength
            "adjusted_score": small_party_score,  # Small parties score is not adjusted
        }
    )

    # caculate total voting behavior
    total_score = sum(entry["adjusted_score"] for entry in voting_behavior)
    for entry in voting_behavior:
        entry["percentage"] = round(
            ((entry["adjusted_score"] / total_score) * 100 if total_score > 0 else 0), 2
        )
        entry["votes"] = int((entry["percentage"] / 100) * eligible_population)

    # sorting
    voting_behavior.sort(key=lambda x: x["votes"], reverse=True)
    return voting_behavior


def create_pop_votes(period_id):
    # get popperiod for voting behavior
    pop_periods = get_entries(PopPeriod, {"period_id": period_id})
    if not pop_periods:
        st.error("No population data available for the selected period.")
        return

    # get voting behavior for each pop
    for pop_period in pop_periods:
        voting_behavior = get_voting_behavior(pop_period)
        # for each party, create a new entry in PopVote
        for entry in voting_behavior:
            data = {
                "period_id": period_id,
                "pop_id": pop_period["pop_id"],
                "party_id": entry["party_id"],
                "votes": entry["votes"],
            }
            # check if entry already exists
            existing_entry = get_entries(
                PopVote,
                {
                    "period_id": period_id,
                    "pop_id": pop_period["pop_id"],
                    "party_id": entry["party_id"],
                },
            )
            if existing_entry:
                # updating entry
                entry_id = existing_entry[0]["id"]
                update_entry(PopVote, entry_id, data)
            else:
                # creating new entry
                create_new_entry(PopVote, data)


def create_election_results(period_id, seats, threshold):
    # get popvotes for voting behavior
    pop_votes = get_entries(PopVote, {"period_id": period_id})
    if not pop_votes:
        st.error("No population voting data available for the selected period.")
        return

    # get sum of all votes
    sum_votes = sum(entry["votes"] for entry in pop_votes)

    # get list of participating parties
    participating_parties = list(
        set([entry["party_id"] for entry in pop_votes if entry["votes"] > 0])
    )
    votes_in_parliament = sum(
        entry["votes"]
        for party_id in participating_parties
        for entry in pop_votes
        if entry["party_id"] == party_id
        and (sum_votes > 0 and (entry["votes"] / sum_votes * 100) >= threshold)
        and party_id >= 0
    )

    # for each party, create data dict
    for party_id in participating_parties:
        # get votes for party
        party_votes = sum(
            entry["votes"] for entry in pop_votes if entry["party_id"] == party_id
        )
        # calculate percentage
        percentage = (party_votes / sum_votes * 100) if sum_votes > 0 else 0.0

        # check for threshold
        if percentage < threshold or party_id < 0:
            in_parliament = False
        else:
            in_parliament = True

        # create data dict
        data = {
            "period_id": period_id,
            "party_id": party_id,
            "votes": party_votes,
            "percentage": round(percentage, 2),
            "in_parliament": in_parliament,
            "in_government": False,  # default value
        }

        # check if entry already exists
        existing_entry = get_entries(
            ElectionResult,
            {"period_id": period_id, "party_id": party_id},
        )
        if existing_entry:
            # if exists, update entry
            entry_id = existing_entry[0]["id"]
            update_entry(ElectionResult, entry_id, data)
        else:
            # if not exists, create new entry
            create_new_entry(ElectionResult, data)
    calculate_seats(period_id, seats)


def calculate_seats(period_id, seats):
    # get election results
    election_results = get_entries(ElectionResult, {"period_id": period_id})
    if not election_results:
        st.error("No election results available for the selected period.")
        return

    # filter for parties in parliament
    parliament = [entry for entry in election_results if entry["in_parliament"]]
    if not parliament:
        st.warning("No parties in parliament for the selected period.")
        return

    # calculate total votes in parliament
    total_votes = sum(entry["votes"] for entry in parliament)

    seats_left_to_allocate = seats

    # calculate seats for each party (rounded seats)
    for entry in parliament:
        relative_votes = entry["votes"] / total_votes if total_votes > 0 else 0
        exact_no_seats = relative_votes * seats
        min_seats = int(exact_no_seats)
        residual_seats = exact_no_seats - min_seats
        entry["residual_seats"] = residual_seats
        entry["seats"] = min_seats
        seats_left_to_allocate -= min_seats

    # allocate the residual seats
    while seats_left_to_allocate > 0:
        # find party with highest residual seats
        max_residual_party = max(parliament, key=lambda x: x["residual_seats"])
        max_residual_party["seats"] += 1
        max_residual_party["residual_seats"] -= 1
        seats_left_to_allocate -= 1

    # update parliament entries
    for entry in parliament:
        data = {"seats": entry["seats"]}
        update_entry(ElectionResult, entry["id"], data)
