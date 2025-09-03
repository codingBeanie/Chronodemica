from typing import List, Dict, Any
from sqlmodel import Session
import numpy as np
from fastapi import HTTPException
from models import Pop, Party, PopPeriod, PartyPeriod, PopVote, ElectionResult, Period
from crud import get_items, create_item, update_item, get_item


def get_distance(pop_period: Dict[str, Any], party_period: Dict[str, Any]) -> int:
    pop_social = pop_period["social_orientation"]
    pop_economic = pop_period["economic_orientation"]
    party_social = party_period["social_orientation"]
    party_economic = party_period["economic_orientation"]
    
    # calculate distance
    distance_ratio = calculate_distance(
        pop_social, pop_economic, party_social, party_economic, ratio=True
    )
    return distance_ratio


def calculate_distance(social_1: int, economic_1: int, social_2: int, economic_2: int, ratio: bool = True) -> float:
    # calculate distance
    distance = np.sqrt((social_1 - social_2) ** 2 + (economic_1 - economic_2) ** 2)
    if not ratio:
        return distance

    # normalize distance to a percentage (0-100)
    # Max distance in 2D space with coordinates from -100 to 100 is sqrt(200^2 + 200^2) = 282.8427
    distance_ratio = int((distance / 282.8427 if distance != 0 else 0) * 100)
    return distance_ratio


def calculate_score(pop_period: Dict[str, Any], distance: float) -> int:
    # extract parameters
    max_distance = pop_period["max_political_distance"]
    variety = pop_period["variety_tolerance"] / 2

    # max distance cap
    if distance > max_distance:
        return 0

    # calculate using Gauss function
    score = np.exp(-(distance**2) / (2 * variety**2))

    # round to integer
    rounded_score = int(np.round(score * 100))

    return rounded_score


def calculate_adjusted_score(party_period: Dict[str, Any], score: int) -> int:
    # extract parameters
    strength = party_period["political_strength"]
    # Linear function with negative score adjustment below 50
    strength_modifier = np.interp(strength, [0, 100], [0.05, 1.5])
    adjusted_score = int(score * strength_modifier)

    return adjusted_score


def get_voting_behavior(db: Session, pop_period: Dict[str, Any]) -> List[Dict[str, Any]]:
    # extract parameters
    pop_id = pop_period["pop_id"]
    period_id = pop_period["period_id"]

    # get reference models
    pop = get_item(db, Pop, pop_id)
    period = get_item(db, Period, period_id)
    party_periods = get_items(db, PartyPeriod, filters={"period_id": period_id})
    
    if not pop or not period:
        raise HTTPException(status_code=404, detail="Pop or Period not found")

    # get additional data
    pop_name = pop.name
    pop_population = pop_period["pop_size"]
    ratio_eligible = pop_period["ratio_eligible"]
    eligible_population = int((pop_population * ratio_eligible) / 100)

    # create return data structure
    voting_behavior = []
    for party_period in party_periods:
        # get reference data
        party_id = party_period.party_id
        party = get_item(db, Party, party_id)
        if not party:
            continue

        # Convert SQLModel object to dict for compatibility with existing functions
        party_period_dict = {
            "social_orientation": party_period.social_orientation,
            "economic_orientation": party_period.economic_orientation,
            "political_strength": party_period.political_strength
        }
        
        distance = get_distance(pop_period, party_period_dict)
        raw_score = calculate_score(pop_period, distance)
        adjusted_score = calculate_adjusted_score(party_period_dict, raw_score)

        # create line data
        line_data = {
            "pop_id": pop_id,
            "pop_name": pop_name,
            "period_id": period_id,
            "party_id": party_id,
            "party_name": party.name,
            "party_full_name": party.full_name,
            "distance": distance,
            "raw_score": raw_score,
            "strength": party_period.political_strength,
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


def create_pop_votes(db: Session, period_id: int) -> None:
    # get popperiod for voting behavior
    pop_periods = get_items(db, PopPeriod, filters={"period_id": period_id})
    if not pop_periods:
        raise HTTPException(status_code=404, detail="No population data available for the selected period")

    # get voting behavior for each pop
    for pop_period in pop_periods:
        # Convert SQLModel object to dict for compatibility with existing functions
        pop_period_dict = {
            "pop_id": pop_period.pop_id,
            "period_id": pop_period.period_id,
            "social_orientation": pop_period.social_orientation,
            "economic_orientation": pop_period.economic_orientation,
            "max_political_distance": pop_period.max_political_distance,
            "variety_tolerance": pop_period.variety_tolerance,
            "non_voters_distance": pop_period.non_voters_distance,
            "small_party_distance": pop_period.small_party_distance,
            "ratio_eligible": pop_period.ratio_eligible,
            "pop_size": pop_period.pop_size
        }
        
        voting_behavior = get_voting_behavior(db, pop_period_dict)
        
        # for each party, create a new entry in PopVote
        for entry in voting_behavior:
            # check if entry already exists
            existing_entries = get_items(
                db, PopVote,
                filters={
                    "period_id": period_id,
                    "pop_id": pop_period.pop_id,
                    "party_id": entry["party_id"],
                }
            )
            
            vote_data = {
                "period_id": period_id,
                "pop_id": pop_period.pop_id,
                "party_id": entry["party_id"],
                "votes": entry["votes"],
            }
            
            if existing_entries:
                # updating entry
                existing_entry = existing_entries[0]
                update_item(db, existing_entry, vote_data)
            else:
                # creating new entry
                new_vote = PopVote(**vote_data)
                create_item(db, new_vote)


def create_election_results(db: Session, period_id: int, seats: int, threshold: float) -> None:
    # get popvotes for voting behavior
    pop_votes = get_items(db, PopVote, filters={"period_id": period_id})
    if not pop_votes:
        raise HTTPException(status_code=404, detail="No population voting data available for the selected period")

    # get sum of all votes
    sum_votes = sum(vote.votes for vote in pop_votes)

    # get list of participating parties
    participating_parties = list(
        set([vote.party_id for vote in pop_votes if vote.votes > 0])
    )

    # for each party, create data dict
    for party_id in participating_parties:
        # get votes for party
        party_votes = sum(
            vote.votes for vote in pop_votes if vote.party_id == party_id
        )
        # calculate percentage
        percentage = (party_votes / sum_votes * 100) if sum_votes > 0 else 0.0

        # check for threshold
        if percentage < threshold or party_id < 0:
            in_parliament = False
        else:
            in_parliament = True

        # create data dict
        result_data = {
            "period_id": period_id,
            "party_id": party_id,
            "votes": party_votes,
            "percentage": round(percentage, 2),
            "in_parliament": in_parliament,
            "in_government": False,  # default value
        }

        # check if entry already exists
        existing_entries = get_items(
            db, ElectionResult,
            filters={"period_id": period_id, "party_id": party_id}
        )
        
        if existing_entries:
            # if exists, update entry
            existing_entry = existing_entries[0]
            update_item(db, existing_entry, result_data)
        else:
            # if not exists, create new entry
            new_result = ElectionResult(**result_data)
            create_item(db, new_result)
            
    calculate_seats(db, period_id, seats)


def calculate_seats(db: Session, period_id: int, seats: int) -> None:
    # get election results
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})
    if not election_results:
        raise HTTPException(status_code=404, detail="No election results available for the selected period")

    # filter for parties in parliament
    parliament = [result for result in election_results if result.in_parliament]
    if not parliament:
        raise HTTPException(status_code=404, detail="No parties in parliament for the selected period")

    # calculate total votes in parliament
    total_votes = sum(result.votes for result in parliament)

    seats_left_to_allocate = seats
    parliament_data = []

    # calculate seats for each party (rounded seats)
    for result in parliament:
        relative_votes = result.votes / total_votes if total_votes > 0 else 0
        exact_no_seats = relative_votes * seats
        min_seats = int(exact_no_seats)
        residual_seats = exact_no_seats - min_seats
        
        party_data = {
            "result": result,
            "residual_seats": residual_seats,
            "seats": min_seats
        }
        parliament_data.append(party_data)
        seats_left_to_allocate -= min_seats

    # allocate the residual seats
    while seats_left_to_allocate > 0:
        # find party with highest residual seats
        max_residual_party = max(parliament_data, key=lambda x: x["residual_seats"])
        max_residual_party["seats"] += 1
        max_residual_party["residual_seats"] -= 1
        seats_left_to_allocate -= 1

    # update parliament entries
    for party_data in parliament_data:
        result = party_data["result"]
        update_data = {"seats": party_data["seats"]}
        update_item(db, result, update_data)
