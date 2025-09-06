from typing import List, Dict, Any
from sqlmodel import Session
import numpy as np
from itertools import combinations
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


def calculate_distance(
    social_1: int, economic_1: int, social_2: int, economic_2: int, ratio: bool = True
) -> float:
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


def get_voting_behavior(
    db: Session, pop_period: Dict[str, Any]
) -> List[Dict[str, Any]]:
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
    eligible_population = int((pop_population * ratio_eligible) / 100) * 1000

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
            "political_strength": party_period.political_strength,
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
        raise HTTPException(
            status_code=404,
            detail="No population data available for the selected period",
        )

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
            "pop_size": pop_period.pop_size,
        }

        voting_behavior = get_voting_behavior(db, pop_period_dict)

        # for each party, create a new entry in PopVote
        for entry in voting_behavior:
            # check if entry already exists
            existing_entries = get_items(
                db,
                PopVote,
                filters={
                    "period_id": period_id,
                    "pop_id": pop_period.pop_id,
                    "party_id": entry["party_id"],
                },
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


def create_election_results(
    db: Session, period_id: int, seats: int, threshold: float
) -> None:
    # get popvotes for voting behavior
    pop_votes = get_items(db, PopVote, filters={"period_id": period_id})
    if not pop_votes:
        raise HTTPException(
            status_code=404,
            detail="No population voting data available for the selected period",
        )

    # get sum of all votes
    sum_votes = sum(vote.votes for vote in pop_votes)

    # get list of participating parties
    participating_parties = list(
        set([vote.party_id for vote in pop_votes if vote.votes > 0])
    )

    # for each party, create data dict
    for party_id in participating_parties:
        # get votes for party
        party_votes = sum(vote.votes for vote in pop_votes if vote.party_id == party_id)
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
            db, ElectionResult, filters={"period_id": period_id, "party_id": party_id}
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
        raise HTTPException(
            status_code=404,
            detail="No election results available for the selected period",
        )

    # filter for parties in parliament
    parliament = [result for result in election_results if result.in_parliament]
    if not parliament:
        raise HTTPException(
            status_code=404, detail="No parties in parliament for the selected period"
        )

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
            "seats": min_seats,
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


def get_distance_scoring_curve(pop_period: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculate scoring curve for distances 0-100 for a given PopPeriod."""
    scoring_data = []

    for distance in range(101):  # 0 to 100 inclusive
        score = calculate_score(pop_period, distance)
        scoring_data.append({"distance": distance, "score": score})

    return scoring_data


def _validate_simulation_prerequisites(db: Session, period_id: int) -> None:
    """Validate that all necessary data exists for simulation."""
    # Check if period exists
    period = get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail=f"Period {period_id} not found")
    
    # Check if PopPeriods exist
    pop_periods = get_items(db, PopPeriod, filters={"period_id": period_id})
    if not pop_periods:
        raise HTTPException(
            status_code=400,
            detail=f"No PopPeriod data found for period {period_id}. Cannot simulate without population data."
        )
    
    # Check if PartyPeriods exist
    party_periods = get_items(db, PartyPeriod, filters={"period_id": period_id})
    if not party_periods:
        raise HTTPException(
            status_code=400,
            detail=f"No PartyPeriod data found for period {period_id}. Cannot simulate without party data."
        )


def run_complete_simulation(
    db: Session, period_id: int, seats: int, threshold: float
) -> Dict[str, Any]:
    """
    Run complete election simulation for a period.
    
    This function orchestrates all simulation steps:
    1. Validates prerequisites (PopPeriods, PartyPeriods exist)
    2. Creates PopVotes based on voting behavior calculations
    3. Creates ElectionResults with seat allocation
    4. Returns comprehensive simulation statistics
    
    Args:
        db: Database session
        period_id: Period to simulate
        seats: Total number of parliament seats
        threshold: Minimum percentage to enter parliament
        
    Returns:
        Dict with simulation results and statistics
    """
    # Validate prerequisites
    _validate_simulation_prerequisites(db, period_id)
    
    # Step 1: Create pop votes
    create_pop_votes(db, period_id)
    
    # Step 2: Create election results with integrated seat calculation
    create_election_results(db, period_id, seats, threshold)
    
    # Gather statistics for return
    pop_votes = get_items(db, PopVote, filters={"period_id": period_id})
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})
    
    # Calculate totals
    total_votes = sum(vote.votes for vote in pop_votes)
    parties_in_parliament = len([r for r in election_results if r.in_parliament])
    total_parties = len([r for r in election_results if r.party_id > 0])  # Exclude non-voters/small parties
    
    return {
        "success": True,
        "message": f"Complete simulation finished for period {period_id}",
        "period_id": period_id,
        "parameters": {
            "seats": seats,
            "threshold": threshold
        },
        "statistics": {
            "total_votes": total_votes,
            "total_parties": total_parties,
            "parties_in_parliament": parties_in_parliament,
            "parliament_threshold_met": parties_in_parliament > 0
        }
    }


def calculate_average_coalition_distance(party_ids: List[int], party_orientations: Dict[int, Dict[str, int]]) -> float:
    """
    Calculate the average political distance between all parties in a coalition.
    
    Args:
        party_ids: List of party IDs in the coalition
        party_orientations: Dict mapping party IDs to their political orientations
        
    Returns:
        Average distance between all party pairs in the coalition
    """
    if len(party_ids) <= 1:
        return 0.0
    
    total_distance = 0.0
    pair_count = 0
    
    # Calculate distance between each pair of parties
    for i in range(len(party_ids)):
        for j in range(i + 1, len(party_ids)):
            party1_id = party_ids[i]
            party2_id = party_ids[j]
            
            # Get orientations for both parties
            if party1_id in party_orientations and party2_id in party_orientations:
                party1_orient = party_orientations[party1_id]
                party2_orient = party_orientations[party2_id]
                
                # Calculate distance using the existing calculate_distance function
                distance = calculate_distance(
                    party1_orient["social_orientation"],
                    party1_orient["economic_orientation"],
                    party2_orient["social_orientation"],
                    party2_orient["economic_orientation"],
                    ratio=False  # Get raw distance, not percentage
                )
                
                total_distance += distance
                pair_count += 1
    
    return total_distance / pair_count if pair_count > 0 else 0.0


def getCoalitions(db: Session, period_id: int) -> List[Dict[str, Any]]:
    """
    Find all possible coalitions that have a majority of seats for a given period.
    
    Args:
        db: Database session
        period_id: Period to analyze for coalitions
        
    Returns:
        List of coalition dictionaries with party details and total seats
    """
    # Get election results for the period
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})
    if not election_results:
        raise HTTPException(
            status_code=404,
            detail=f"No election results found for period {period_id}"
        )
    
    # Filter for parties with seats (in parliament)
    parties_with_seats = [result for result in election_results if result.seats > 0 and result.party_id > 0]
    if not parties_with_seats:
        raise HTTPException(
            status_code=404,
            detail=f"No parties with seats found for period {period_id}"
        )
    
    # Calculate total seats in parliament
    total_seats = sum(result.seats for result in parties_with_seats)
    majority_threshold = total_seats // 2 + 1
    
    # Get party details and political orientations for enriched coalition information
    party_details = {}
    party_orientations = {}
    
    for result in parties_with_seats:
        party = get_item(db, Party, result.party_id)
        if party:
            party_details[result.party_id] = {
                "name": party.name,
                "full_name": party.full_name,
                "color": party.color
            }
        
        # Get party period data for political orientations
        party_periods = get_items(db, PartyPeriod, filters={"period_id": period_id, "party_id": result.party_id})
        if party_periods:
            party_period = party_periods[0]
            party_orientations[result.party_id] = {
                "social_orientation": party_period.social_orientation,
                "economic_orientation": party_period.economic_orientation
            }
    
    coalitions = []
    
    # Generate all possible combinations of parties (from 1 to all parties)
    for size in range(1, len(parties_with_seats) + 1):
        for combination in combinations(parties_with_seats, size):
            # Calculate total seats for this combination
            coalition_seats = sum(party.seats for party in combination)
            
            # Check if coalition has majority
            if coalition_seats >= majority_threshold:
                coalition_parties = []
                party_ids_in_coalition = []
                
                for party in combination:
                    party_info = party_details.get(party.party_id, {
                        "name": f"Party {party.party_id}",
                        "full_name": f"Party {party.party_id}",
                        "color": "#525252"
                    })
                    
                    coalition_parties.append({
                        "party_id": party.party_id,
                        "name": party_info["name"],
                        "full_name": party_info["full_name"],
                        "color": party_info["color"],
                        "seats": party.seats,
                        "percentage": party.percentage,
                        "in_government": party.in_government,
                        "head_of_government": party.head_of_government
                    })
                    party_ids_in_coalition.append(party.party_id)
                
                # Calculate average distance between all parties in the coalition
                avg_distance = calculate_average_coalition_distance(party_ids_in_coalition, party_orientations)
                
                # Generate coalition name based on party names sorted by seat share
                coalition_parties_sorted = sorted(coalition_parties, key=lambda x: x["seats"], reverse=True)
                party_names = [party["name"] for party in coalition_parties_sorted]
                coalition_name = "-".join(party_names) + " Coalition"
                
                coalition = {
                    "coalition_id": len(coalitions) + 1,
                    "coalition_name": coalition_name,
                    "parties": coalition_parties,
                    "total_seats": coalition_seats,
                    "total_percentage": sum(party.percentage for party in combination),
                    "party_count": len(combination),
                    "majority_margin": coalition_seats - majority_threshold + 1,
                    "average_distance": avg_distance
                }
                
                coalitions.append(coalition)
    
    # Sort coalitions first by party count (ascending), then by average distance (ascending)
    coalitions.sort(key=lambda x: (x["party_count"], x["average_distance"]))
    
    return coalitions
