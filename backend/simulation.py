from typing import List, Dict, Any
from sqlmodel import Session
import numpy as np
from itertools import combinations
from fastapi import HTTPException
from models import Pop, Party, PopPeriod, PartyPeriod, PopVote, ElectionResult, Period
from crud import get_items, create_item, update_item, get_item


# Constants for configuration
MAX_DISTANCE_2D = 282.8427  # sqrt(200^2 + 200^2) for -100 to 100 coordinates
SPECIAL_PARTY_IDS = {"NON_VOTERS": -1, "SMALL_PARTIES": -2}

SPECIAL_PARTIES_CONFIG = {
    SPECIAL_PARTY_IDS["NON_VOTERS"]: {
        "name": "Non-Voters",
        "full_name": "Non-Voters",
        "strength": 0,
    },
    SPECIAL_PARTY_IDS["SMALL_PARTIES"]: {
        "name": "Small Parties",
        "full_name": "Small Parties",
        "strength": 0,
    },
}


def calculate_distance(
    social_1: int, economic_1: int, social_2: int, economic_2: int, ratio: bool = True
) -> float:
    """Calculate Euclidean distance between two political positions."""
    distance = np.sqrt((social_1 - social_2) ** 2 + (economic_1 - economic_2) ** 2)

    if not ratio:
        return distance

    # Normalize distance to percentage (0-100)
    distance_ratio = int((distance / MAX_DISTANCE_2D if distance != 0 else 0) * 100)
    return distance_ratio


def calculate_score(max_distance: int, variety_tolerance: int, distance: float) -> int:
    """Calculate voting score using Gaussian function based on political distance."""
    # Max distance cap
    if distance > max_distance:
        return 0

    # Calculate using Gauss function
    variety = variety_tolerance / 2
    score = np.exp(-(distance**2) / (2 * variety**2))

    return int(np.round(score * 100))


def calculate_adjusted_score(political_strength: int, score: int) -> int:
    """Apply political strength modifier to raw voting score."""
    strength_modifier = np.interp(political_strength, [0, 100], [0.05, 1.5])
    return int(score * strength_modifier)


def convert_sqlmodel_to_dict(obj, fields: List[str]) -> Dict[str, Any]:
    """Convert SQLModel object to dictionary with specified fields."""
    return {field: getattr(obj, field) for field in fields}


def create_voting_entry(
    pop_data: Dict[str, Any], party_data: Dict[str, Any], party_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a single voting behavior entry."""
    distance = calculate_distance(
        pop_data["social_orientation"],
        pop_data["economic_orientation"],
        party_data["social_orientation"],
        party_data["economic_orientation"],
    )

    raw_score = calculate_score(
        pop_data["max_political_distance"], pop_data["variety_tolerance"], distance
    )

    adjusted_score = calculate_adjusted_score(
        party_data.get("political_strength", 0), raw_score
    )

    return {
        "pop_id": pop_data["pop_id"],
        "pop_name": pop_data["pop_name"],
        "period_id": pop_data["period_id"],
        "party_id": party_info["party_id"],
        "party_name": party_info["party_name"],
        "party_full_name": party_info["party_full_name"],
        "distance": distance,
        "raw_score": raw_score,
        "strength": party_data.get("political_strength", 0),
        "adjusted_score": adjusted_score,
    }


def add_special_parties_voting(pop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Add voting behavior for non-voters and small parties."""
    special_entries = []

    for party_id, config in SPECIAL_PARTIES_CONFIG.items():
        distance_key = (
            "non_voters_distance"
            if party_id == SPECIAL_PARTY_IDS["NON_VOTERS"]
            else "small_party_distance"
        )
        distance = pop_data[distance_key]

        score = calculate_score(
            pop_data["max_political_distance"], pop_data["variety_tolerance"], distance
        )

        entry = {
            "pop_id": pop_data["pop_id"],
            "pop_name": pop_data["pop_name"],
            "period_id": pop_data["period_id"],
            "party_id": party_id,
            "party_name": config["name"],
            "party_full_name": config["full_name"],
            "distance": distance,
            "raw_score": score,
            "strength": config["strength"],
            "adjusted_score": score,  # Special parties don't get strength adjustment
        }
        special_entries.append(entry)

    return special_entries


def calculate_vote_percentages_and_votes(
    voting_behavior: List[Dict[str, Any]], eligible_population: int
) -> List[Dict[str, Any]]:
    """Calculate percentages and vote counts for all voting behavior entries."""
    total_score = sum(entry["adjusted_score"] for entry in voting_behavior)

    for entry in voting_behavior:
        percentage = (
            (entry["adjusted_score"] / total_score * 100) if total_score > 0 else 0
        )
        entry["percentage"] = round(percentage, 2)
        entry["votes"] = int((percentage / 100) * eligible_population)

    # Sort by votes descending
    voting_behavior.sort(key=lambda x: x["votes"], reverse=True)
    return voting_behavior


def get_voting_behavior(
    db: Session, pop_period: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Calculate complete voting behavior for a population in a period."""
    pop_id = pop_period["pop_id"]
    period_id = pop_period["period_id"]

    # Get reference models
    pop = get_item(db, Pop, pop_id)
    period = get_item(db, Period, period_id)
    party_periods = get_items(db, PartyPeriod, filters={"period_id": period_id})

    if not pop or not period:
        raise HTTPException(status_code=404, detail="Pop or Period not found")

    # Calculate eligible population
    pop_population = pop_period["pop_size"]
    ratio_eligible = pop_period["ratio_eligible"]
    eligible_population = int((pop_population * ratio_eligible) / 100) * 1000

    # Add pop name to data
    pop_data = {**pop_period, "pop_name": pop.name}

    # Create voting behavior entries for regular parties
    voting_behavior = []
    for party_period in party_periods:
        party = get_item(db, Party, party_period.party_id)
        if not party:
            continue

        party_data = convert_sqlmodel_to_dict(
            party_period,
            ["social_orientation", "economic_orientation", "political_strength"],
        )

        party_info = {
            "party_id": party_period.party_id,
            "party_name": party.name,
            "party_full_name": party.full_name,
        }

        entry = create_voting_entry(pop_data, party_data, party_info)
        voting_behavior.append(entry)

    # Add special parties (non-voters, small parties)
    special_entries = add_special_parties_voting(pop_data)
    voting_behavior.extend(special_entries)

    # Calculate final percentages and votes
    return calculate_vote_percentages_and_votes(voting_behavior, eligible_population)


def upsert_pop_vote(db: Session, vote_data: Dict[str, Any]) -> None:
    """Create or update a PopVote entry."""
    existing_entries = get_items(
        db,
        PopVote,
        filters={
            "period_id": vote_data["period_id"],
            "pop_id": vote_data["pop_id"],
            "party_id": vote_data["party_id"],
        },
    )

    if existing_entries:
        update_item(db, existing_entries[0], vote_data)
    else:
        new_vote = PopVote(**vote_data)
        create_item(db, new_vote)


def create_pop_votes(db: Session, period_id: int) -> None:
    """Create PopVotes for all populations in a period."""
    pop_periods = get_items(db, PopPeriod, filters={"period_id": period_id})
    if not pop_periods:
        raise HTTPException(
            status_code=404,
            detail="No population data available for the selected period",
        )

    for pop_period in pop_periods:
        pop_period_dict = convert_sqlmodel_to_dict(
            pop_period,
            [
                "pop_id",
                "period_id",
                "social_orientation",
                "economic_orientation",
                "max_political_distance",
                "variety_tolerance",
                "non_voters_distance",
                "small_party_distance",
                "ratio_eligible",
                "pop_size",
            ],
        )

        voting_behavior = get_voting_behavior(db, pop_period_dict)

        for entry in voting_behavior:
            vote_data = {
                "period_id": period_id,
                "pop_id": pop_period.pop_id,
                "party_id": entry["party_id"],
                "votes": entry["votes"],
            }
            upsert_pop_vote(db, vote_data)


def calculate_election_result_data(
    party_id: int, party_votes: int, sum_votes: int, threshold: float
) -> Dict[str, Any]:
    """Calculate election result data for a single party."""
    percentage = (party_votes / sum_votes * 100) if sum_votes > 0 else 0.0
    in_parliament = percentage >= threshold and party_id > 0

    return {
        "period_id": None,  # Will be set by caller
        "party_id": party_id,
        "votes": party_votes,
        "percentage": round(percentage, 2),
        "in_parliament": in_parliament,
        "in_government": False,  # Default value
    }


def upsert_election_result(db: Session, result_data: Dict[str, Any]) -> None:
    """Create or update an ElectionResult entry."""
    existing_entries = get_items(
        db,
        ElectionResult,
        filters={
            "period_id": result_data["period_id"],
            "party_id": result_data["party_id"],
        },
    )

    if existing_entries:
        update_item(db, existing_entries[0], result_data)
    else:
        new_result = ElectionResult(**result_data)
        create_item(db, new_result)


def get_party_votes_summary(pop_votes: List[PopVote]) -> Dict[int, int]:
    """Get total votes per party from PopVote entries."""
    party_votes = {}
    for vote in pop_votes:
        if vote.party_id not in party_votes:
            party_votes[vote.party_id] = 0
        party_votes[vote.party_id] += vote.votes

    # Filter out parties with zero votes
    return {party_id: votes for party_id, votes in party_votes.items() if votes > 0}


def create_election_results(
    db: Session, period_id: int, seats: int, threshold: float
) -> None:
    """Create election results and calculate seats for a period."""
    pop_votes = get_items(db, PopVote, filters={"period_id": period_id})
    if not pop_votes:
        raise HTTPException(
            status_code=404,
            detail="No population voting data available for the selected period",
        )

    sum_votes = sum(vote.votes for vote in pop_votes)
    party_votes_summary = get_party_votes_summary(pop_votes)

    for party_id, party_votes in party_votes_summary.items():
        result_data = calculate_election_result_data(
            party_id, party_votes, sum_votes, threshold
        )
        result_data["period_id"] = period_id
        upsert_election_result(db, result_data)

    calculate_seats(db, period_id, seats)


def allocate_residual_seats(
    parliament_data: List[Dict[str, Any]], seats_left: int
) -> None:
    """Allocate remaining seats using largest remainder method."""
    while seats_left > 0:
        # Find party with highest residual seats
        max_residual_party = max(parliament_data, key=lambda x: x["residual_seats"])
        max_residual_party["seats"] += 1
        max_residual_party["residual_seats"] -= 1
        seats_left -= 1


def calculate_seats(db: Session, period_id: int, seats: int) -> None:
    """Calculate seat allocation using largest remainder method."""
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})
    if not election_results:
        raise HTTPException(
            status_code=404,
            detail="No election results available for the selected period",
        )

    # Filter for parties in parliament (above threshold)
    parliament = [result for result in election_results if result.in_parliament]
    if not parliament:
        raise HTTPException(
            status_code=404, detail="No parties in parliament for the selected period"
        )

    # Calculate seat allocation
    total_votes = sum(result.votes for result in parliament)
    seats_left_to_allocate = seats
    parliament_data = []

    # Calculate minimum seats and residuals for each party
    for result in parliament:
        relative_votes = result.votes / total_votes if total_votes > 0 else 0
        exact_seats = relative_votes * seats
        min_seats = int(exact_seats)
        residual_seats = exact_seats - min_seats

        party_data = {
            "result": result,
            "residual_seats": residual_seats,
            "seats": min_seats,
        }
        parliament_data.append(party_data)
        seats_left_to_allocate -= min_seats

    # Allocate residual seats
    allocate_residual_seats(parliament_data, seats_left_to_allocate)

    # Update database with final seat counts
    for party_data in parliament_data:
        update_data = {"seats": party_data["seats"]}
        update_item(db, party_data["result"], update_data)
    
    # Ensure parties not in parliament have 0 seats
    parties_not_in_parliament = [result for result in election_results if not result.in_parliament]
    for result in parties_not_in_parliament:
        update_data = {"seats": 0}
        update_item(db, result, update_data)


def get_distance_scoring_curve(pop_period: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculate scoring curve for distances 0-100 for a given PopPeriod."""
    return [
        {
            "distance": distance,
            "score": calculate_score(
                pop_period["max_political_distance"],
                pop_period["variety_tolerance"],
                distance,
            ),
        }
        for distance in range(101)  # 0 to 100 inclusive
    ]


def validate_simulation_prerequisites(db: Session, period_id: int) -> None:
    """Validate that all necessary data exists for simulation."""
    period = get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail=f"Period {period_id} not found")

    pop_periods = get_items(db, PopPeriod, filters={"period_id": period_id})
    if not pop_periods:
        raise HTTPException(
            status_code=400,
            detail=f"No PopPeriod data found for period {period_id}. Cannot simulate without population data.",
        )

    party_periods = get_items(db, PartyPeriod, filters={"period_id": period_id})
    if not party_periods:
        raise HTTPException(
            status_code=400,
            detail=f"No PartyPeriod data found for period {period_id}. Cannot simulate without party data.",
        )


def gather_simulation_statistics(db: Session, period_id: int) -> Dict[str, Any]:
    """Gather statistics about the simulation results."""
    pop_votes = get_items(db, PopVote, filters={"period_id": period_id})
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})

    total_votes = sum(vote.votes for vote in pop_votes)
    parties_in_parliament = len([r for r in election_results if r.in_parliament])
    total_parties = len(
        [r for r in election_results if r.party_id > 0]
    )  # Exclude special parties

    return {
        "total_votes": total_votes,
        "total_parties": total_parties,
        "parties_in_parliament": parties_in_parliament,
        "parliament_threshold_met": parties_in_parliament > 0,
    }


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
    """
    validate_simulation_prerequisites(db, period_id)

    # Execute simulation steps
    create_pop_votes(db, period_id)
    create_election_results(db, period_id, seats, threshold)

    statistics = gather_simulation_statistics(db, period_id)

    return {
        "success": True,
        "message": f"Complete simulation finished for period {period_id}",
        "period_id": period_id,
        "parameters": {"seats": seats, "threshold": threshold},
        "statistics": statistics,
    }


def calculate_average_coalition_distance(
    party_ids: List[int], party_orientations: Dict[int, Dict[str, int]]
) -> float:
    """Calculate the average political distance between all parties in a coalition."""
    if len(party_ids) <= 1:
        return 0.0

    distances = []
    for i in range(len(party_ids)):
        for j in range(i + 1, len(party_ids)):
            party1_id, party2_id = party_ids[i], party_ids[j]

            if party1_id in party_orientations and party2_id in party_orientations:
                party1_orient = party_orientations[party1_id]
                party2_orient = party_orientations[party2_id]

                distance = calculate_distance(
                    party1_orient["social_orientation"],
                    party1_orient["economic_orientation"],
                    party2_orient["social_orientation"],
                    party2_orient["economic_orientation"],
                    ratio=False,
                )
                distances.append(distance)

    return sum(distances) / len(distances) if distances else 0.0


def get_party_details_and_orientations(
    db: Session, period_id: int, parties_with_seats: List
) -> tuple[Dict, Dict]:
    """Get party details and political orientations for coalition analysis."""
    party_details = {}
    party_orientations = {}

    for result in parties_with_seats:
        party = get_item(db, Party, result.party_id)
        if party:
            party_details[result.party_id] = {
                "name": party.name,
                "full_name": party.full_name,
                "color": party.color,
            }

        party_periods = get_items(
            db,
            PartyPeriod,
            filters={"period_id": period_id, "party_id": result.party_id},
        )
        if party_periods:
            party_period = party_periods[0]
            party_orientations[result.party_id] = {
                "social_orientation": party_period.social_orientation,
                "economic_orientation": party_period.economic_orientation,
            }

    return party_details, party_orientations


def create_coalition_data(
    combination, party_details: Dict, party_orientations: Dict, coalition_id: int
) -> Dict[str, Any]:
    """Create coalition data structure from party combination."""
    coalition_parties = []
    party_ids = []

    for party in combination:
        party_info = party_details.get(
            party.party_id,
            {
                "name": f"Party {party.party_id}",
                "full_name": f"Party {party.party_id}",
                "color": "#525252",
            },
        )

        coalition_parties.append(
            {
                "party_id": party.party_id,
                "name": party_info["name"],
                "full_name": party_info["full_name"],
                "color": party_info["color"],
                "seats": party.seats,
                "percentage": party.percentage,
                "in_government": party.in_government,
                "head_of_government": party.head_of_government,
            }
        )
        party_ids.append(party.party_id)

    # Calculate coalition metrics
    avg_distance = calculate_average_coalition_distance(party_ids, party_orientations)
    coalition_seats = sum(party.seats for party in combination)

    # Generate coalition name
    coalition_parties_sorted = sorted(
        coalition_parties, key=lambda x: x["seats"], reverse=True
    )
    party_names = [party["name"] for party in coalition_parties_sorted]
    coalition_name = "-".join(party_names) + " Coalition"

    return {
        "coalition_id": coalition_id,
        "coalition_name": coalition_name,
        "parties": coalition_parties,
        "total_seats": coalition_seats,
        "total_percentage": sum(party.percentage for party in combination),
        "party_count": len(combination),
        "majority_margin": coalition_seats
        - (
            sum(party.seats for party in combination for party in [combination[0]]) // 2
            + 1
        )
        + 1,  # This needs fixing
        "average_distance": avg_distance,
    }


def getCoalitions(db: Session, period_id: int) -> List[Dict[str, Any]]:
    """Find all minimal coalitions that have a majority of seats for a given period."""
    election_results = get_items(db, ElectionResult, filters={"period_id": period_id})
    if not election_results:
        raise HTTPException(
            status_code=404, detail=f"No election results found for period {period_id}"
        )

    # Filter for parties with seats (in parliament)
    parties_with_seats = [
        result
        for result in election_results
        if result.seats > 0 and result.party_id > 0
    ]
    if not parties_with_seats:
        raise HTTPException(
            status_code=404,
            detail=f"No parties with seats found for period {period_id}",
        )

    # Calculate majority threshold
    total_seats = sum(result.seats for result in parties_with_seats)
    majority_threshold = total_seats // 2 + 1

    # Get party details and orientations
    party_details, party_orientations = get_party_details_and_orientations(
        db, period_id, parties_with_seats
    )

    coalitions = []
    minimal_coalition_party_sets = []

    # Generate combinations starting with smallest size first
    for size in range(1, len(parties_with_seats) + 1):
        for combination in combinations(parties_with_seats, size):
            coalition_seats = sum(party.seats for party in combination)

            # Check if coalition has majority
            if coalition_seats >= majority_threshold:
                current_party_ids = set(party.party_id for party in combination)

                # Check if this coalition is a superset of any existing minimal coalition
                is_superset = any(
                    minimal_set.issubset(current_party_ids)
                    and minimal_set != current_party_ids
                    for minimal_set in minimal_coalition_party_sets
                )

                # Only add if it's not a superset of an existing minimal coalition
                if not is_superset:
                    coalition = create_coalition_data(
                        combination,
                        party_details,
                        party_orientations,
                        len(coalitions) + 1,
                    )
                    coalition["majority_margin"] = (
                        coalition_seats - majority_threshold + 1
                    )  # Fix the calculation

                    coalitions.append(coalition)
                    minimal_coalition_party_sets.append(current_party_ids)

    # Sort coalitions first by party count (ascending), then by average distance (ascending)
    coalitions.sort(key=lambda x: (x["party_count"], x["average_distance"]))

    return coalitions
