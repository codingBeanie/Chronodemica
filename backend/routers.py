import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
from models import (
    Period, Pop, PopPeriod, Party, PartyPeriod, 
    PopVote, ElectionResult
)
import crud
import statistics
from simulation import create_pop_votes, create_election_results, get_voting_behavior, get_distance_scoring_curve, run_complete_simulation

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronodemica.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

router = APIRouter()


# Period endpoints
@router.post("/period/", response_model=Period)
def create_period(period: Period, db: Session = Depends(get_session)):
    return crud.create_item(db, period)

@router.get("/period/", response_model=List[Period])
def read_periods(
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    year: Optional[int] = Query(None),
    db: Session = Depends(get_session)
):
    filters = {}
    if year is not None:
        filters["year"] = year
    return crud.get_items(db, Period, skip, limit, filters, sort_by, sort_direction)

@router.get("/period/{period_id}", response_model=Period)
def read_period(period_id: int, db: Session = Depends(get_session)):
    period = crud.get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period

@router.put("/period/{period_id}", response_model=Period)
def update_period(period_id: int, period_update: dict, db: Session = Depends(get_session)):
    period = crud.get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return crud.update_item(db, period, period_update)

@router.delete("/period/{period_id}", response_model=Period)
def delete_period(period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Period, period_id)


# Pop endpoints
@router.post("/pop/", response_model=Pop)
def create_pop(pop: Pop, db: Session = Depends(get_session)):
    return crud.create_item(db, pop)

@router.get("/pop/", response_model=List[Pop])
def read_pops(
    period_id: Optional[int] = Query(None, description="Period ID to filter valid pops (optional)"),
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    name: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    from sqlmodel import select
    
    # Build the base query
    statement = select(Pop)
    
    # Apply period-based validation only if period_id is provided
    if period_id is not None:
        # Get the period to retrieve the year
        period = crud.get_item(db, Period, period_id)
        if not period:
            raise HTTPException(status_code=404, detail="Period not found")
        
        # Add period-based validation
        statement = statement.where(
            # Check valid_from: NULL means no start limit, otherwise year must be >= valid_from
            (Pop.valid_from.is_(None)) | (period.year >= Pop.valid_from),
            # Check valid_until: NULL means no end limit, otherwise year must be < valid_until  
            (Pop.valid_until.is_(None)) | (period.year < Pop.valid_until)
        )
    
    # Apply name filter if provided
    if name is not None:
        statement = statement.where(Pop.name == name)
    
    # Apply sorting
    if sort_by and hasattr(Pop, sort_by):
        column = getattr(Pop, sort_by)
        if sort_direction.lower() == "desc":
            statement = statement.order_by(column.desc())
        else:
            statement = statement.order_by(column.asc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    return db.exec(statement).all()

@router.get("/pop/{pop_id}", response_model=Pop)
def read_pop(pop_id: int, db: Session = Depends(get_session)):
    pop = crud.get_item(db, Pop, pop_id)
    if not pop:
        raise HTTPException(status_code=404, detail="Pop not found")
    return pop

@router.put("/pop/{pop_id}", response_model=Pop)
def update_pop(pop_id: int, pop_update: dict, db: Session = Depends(get_session)):
    pop = crud.get_item(db, Pop, pop_id)
    if not pop:
        raise HTTPException(status_code=404, detail="Pop not found")
    return crud.update_item(db, pop, pop_update)

@router.delete("/pop/{pop_id}", response_model=Pop)
def delete_pop(pop_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Pop, pop_id)


# PopPeriod endpoints
@router.post("/pop-period/", response_model=PopPeriod)
def create_pop_period(pop_period: PopPeriod, db: Session = Depends(get_session)):
    return crud.create_item(db, pop_period)

@router.get("/pop-period/", response_model=List[PopPeriod])
def read_pop_periods(
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    pop_id: Optional[int] = Query(None),
    period_id: Optional[int] = Query(None),
    db: Session = Depends(get_session)
):
    filters = {}
    if pop_id is not None:
        filters["pop_id"] = pop_id
    if period_id is not None:
        filters["period_id"] = period_id
    return crud.get_items(db, PopPeriod, skip, limit, filters, sort_by, sort_direction)

@router.get("/pop-period/{pop_period_id}", response_model=PopPeriod)
def read_pop_period(pop_period_id: int, db: Session = Depends(get_session)):
    pop_period = crud.get_item(db, PopPeriod, pop_period_id)
    if not pop_period:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    return pop_period

@router.put("/pop-period/{pop_period_id}", response_model=PopPeriod)
def update_pop_period(pop_period_id: int, pop_period_update: dict, db: Session = Depends(get_session)):
    pop_period = crud.get_item(db, PopPeriod, pop_period_id)
    if not pop_period:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    return crud.update_item(db, pop_period, pop_period_update)

@router.delete("/pop-period/{pop_period_id}", response_model=PopPeriod)
def delete_pop_period(pop_period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PopPeriod, pop_period_id)


# Party endpoints
@router.post("/party/", response_model=Party)
def create_party(party: Party, db: Session = Depends(get_session)):
    return crud.create_item(db, party)

@router.get("/party/", response_model=List[Party])
def read_parties(
    period_id: Optional[int] = Query(None, description="Period ID to filter valid parties (optional)"),
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    name: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    from sqlmodel import select
    
    # Build the base query
    statement = select(Party)
    
    # Apply period-based validation only if period_id is provided
    if period_id is not None:
        # Get the period to retrieve the year
        period = crud.get_item(db, Period, period_id)
        if not period:
            raise HTTPException(status_code=404, detail="Period not found")
        
        # Add period-based validation
        statement = statement.where(
            # Check valid_from: NULL means no start limit, otherwise year must be >= valid_from
            (Party.valid_from.is_(None)) | (period.year >= Party.valid_from),
            # Check valid_until: NULL means no end limit, otherwise year must be < valid_until  
            (Party.valid_until.is_(None)) | (period.year < Party.valid_until)
        )
    
    # Apply name filter if provided
    if name is not None:
        statement = statement.where(Party.name == name)
    
    # Apply sorting
    if sort_by and hasattr(Party, sort_by):
        column = getattr(Party, sort_by)
        if sort_direction.lower() == "desc":
            statement = statement.order_by(column.desc())
        else:
            statement = statement.order_by(column.asc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    return db.exec(statement).all()

@router.get("/party/{party_id}", response_model=Party)
def read_party(party_id: int, db: Session = Depends(get_session)):
    party = crud.get_item(db, Party, party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@router.put("/party/{party_id}", response_model=Party)
def update_party(party_id: int, party_update: dict, db: Session = Depends(get_session)):
    party = crud.get_item(db, Party, party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return crud.update_item(db, party, party_update)

@router.delete("/party/{party_id}", response_model=Party)
def delete_party(party_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Party, party_id)


# PartyPeriod endpoints
@router.post("/party-period/", response_model=PartyPeriod)
def create_party_period(party_period: PartyPeriod, db: Session = Depends(get_session)):
    return crud.create_item(db, party_period)

@router.get("/party-period/", response_model=List[PartyPeriod])
def read_party_periods(
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    party_id: Optional[int] = Query(None),
    period_id: Optional[int] = Query(None),
    db: Session = Depends(get_session)
):
    filters = {}
    if party_id is not None:
        filters["party_id"] = party_id
    if period_id is not None:
        filters["period_id"] = period_id
    return crud.get_items(db, PartyPeriod, skip, limit, filters, sort_by, sort_direction)

@router.get("/party-period/{party_period_id}", response_model=PartyPeriod)
def read_party_period(party_period_id: int, db: Session = Depends(get_session)):
    party_period = crud.get_item(db, PartyPeriod, party_period_id)
    if not party_period:
        raise HTTPException(status_code=404, detail="PartyPeriod not found")
    return party_period

@router.put("/party-period/{party_period_id}", response_model=PartyPeriod)
def update_party_period(party_period_id: int, party_period_update: dict, db: Session = Depends(get_session)):
    party_period = crud.get_item(db, PartyPeriod, party_period_id)
    if not party_period:
        raise HTTPException(status_code=404, detail="PartyPeriod not found")
    return crud.update_item(db, party_period, party_period_update)

@router.delete("/party-period/{party_period_id}", response_model=PartyPeriod)
def delete_party_period(party_period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PartyPeriod, party_period_id)


# PopVote endpoints
@router.post("/pop-vote/", response_model=PopVote)
def create_pop_vote(pop_vote: PopVote, db: Session = Depends(get_session)):
    return crud.create_item(db, pop_vote)

@router.get("/pop-vote/", response_model=List[PopVote])
def read_pop_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, PopVote, skip, limit)

@router.get("/pop-vote/{pop_vote_id}", response_model=PopVote)
def read_pop_vote(pop_vote_id: int, db: Session = Depends(get_session)):
    pop_vote = crud.get_item(db, PopVote, pop_vote_id)
    if not pop_vote:
        raise HTTPException(status_code=404, detail="PopVote not found")
    return pop_vote

@router.put("/pop-vote/{pop_vote_id}", response_model=PopVote)
def update_pop_vote(pop_vote_id: int, pop_vote_update: dict, db: Session = Depends(get_session)):
    pop_vote = crud.get_item(db, PopVote, pop_vote_id)
    if not pop_vote:
        raise HTTPException(status_code=404, detail="PopVote not found")
    return crud.update_item(db, pop_vote, pop_vote_update)

@router.delete("/pop-vote/{pop_vote_id}", response_model=PopVote)
def delete_pop_vote(pop_vote_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PopVote, pop_vote_id)


# ElectionResult endpoints
@router.post("/election-result/", response_model=ElectionResult)
def create_election_result(election_result: ElectionResult, db: Session = Depends(get_session)):
    return crud.create_item(db, election_result)

@router.get("/election-result/", response_model=List[ElectionResult])
def read_election_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, ElectionResult, skip, limit)

@router.get("/election-result/{election_result_id}", response_model=ElectionResult)
def read_election_result(election_result_id: int, db: Session = Depends(get_session)):
    election_result = crud.get_item(db, ElectionResult, election_result_id)
    if not election_result:
        raise HTTPException(status_code=404, detail="ElectionResult not found")
    return election_result

@router.put("/election-result/{election_result_id}", response_model=ElectionResult)
def update_election_result(election_result_id: int, election_result_update: dict, db: Session = Depends(get_session)):
    election_result = crud.get_item(db, ElectionResult, election_result_id)
    if not election_result:
        raise HTTPException(status_code=404, detail="ElectionResult not found")
    return crud.update_item(db, election_result, election_result_update)

@router.delete("/election-result/{election_result_id}", response_model=ElectionResult)
def delete_election_result(election_result_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, ElectionResult, election_result_id)


# Data structure endpoint
@router.get("/data-structure/{model_name}", response_model=Dict[str, Any])
def get_data_structure(model_name: str):
    models_map = {
        "period": Period,
        "pop": Pop,
        "pop-period": PopPeriod,
        "party": Party,
        "party-period": PartyPeriod,
        "pop-vote": PopVote,
        "election-result": ElectionResult
    }
    
    if model_name.lower() not in models_map:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    model = models_map[model_name.lower()]
    
    # Get model fields and their types
    fields = {}
    for field_name, field_info in model.model_fields.items():
        field_type = str(field_info.annotation)
        # Clean up the type string for better readability
        field_type = field_type.replace("typing.", "").replace("<class '", "").replace("'>", "")
        
        # Handle default value safely
        default_value = None
        if hasattr(field_info, 'default'):
            try:
                # Check if default is PydanticUndefined or similar non-serializable type
                from pydantic_core import PydanticUndefined
                if field_info.default is not PydanticUndefined:
                    default_value = field_info.default
            except ImportError:
                # Fallback for older pydantic versions
                if str(type(field_info.default)) != "<class 'pydantic_core._pydantic_core.PydanticUndefinedType'>":
                    default_value = field_info.default
        
        fields[field_name] = {
            "type": field_type,
            "required": field_info.is_required(),
            "default": default_value
        }
    
    return {
        "model": model_name,
        "table_name": model.__tablename__,
        "columns": list(fields.keys()),
        "fields": fields
    }


# Statistics endpoints
@router.get("/statistics/period/{period_id}/pop-size", response_model=Dict[str, Any])
def get_period_pop_size_statistics(period_id: int, db: Session = Depends(get_session)):
    """Get total pop_size statistics for a specific period."""
    return statistics.get_pop_size_sum(db, period_id)


# Simulation endpoints
@router.post("/simulation/period/{period_id}/pop-votes")
def simulate_pop_votes(period_id: int, db: Session = Depends(get_session)):
    """Generate voting behavior for all populations in a period."""
    create_pop_votes(db, period_id)
    return {"message": f"Pop votes created for period {period_id}"}


@router.post("/simulation/period/{period_id}/election-results")
def simulate_election_results(
    period_id: int, 
    seats: int,
    threshold: float,
    db: Session = Depends(get_session)
):
    """Generate election results and seat allocation for a period."""
    create_election_results(db, period_id, seats, threshold)
    return {
        "message": f"Election results created for period {period_id}",
        "seats": seats,
        "threshold": threshold
    }


@router.post("/simulation/period/{period_id}/full-simulation")
def run_full_simulation(
    period_id: int,
    seats: int,
    threshold: float,
    db: Session = Depends(get_session)
):
    """Run complete simulation with validation and comprehensive results."""
    return run_complete_simulation(db, period_id, seats, threshold)


@router.get("/simulation/period/{period_id}/pop/{pop_id}/voting-behavior", response_model=List[Dict[str, Any]])
def get_pop_voting_behavior(
    period_id: int, 
    pop_id: int, 
    db: Session = Depends(get_session)
):
    """Get detailed voting behavior for a specific population in a period."""
    # Get the PopPeriod entry
    pop_periods = crud.get_items(db, PopPeriod, filters={"period_id": period_id, "pop_id": pop_id})
    if not pop_periods:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    
    pop_period = pop_periods[0]
    
    # Convert to dict for compatibility
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
    
    return get_voting_behavior(db, pop_period_dict)


@router.get("/simulation/period/{period_id}/results", response_model=List[ElectionResult])
def get_simulation_results(period_id: int, db: Session = Depends(get_session)):
    """Get election results for a period."""
    results = crud.get_items(db, ElectionResult, filters={"period_id": period_id})
    if not results:
        raise HTTPException(status_code=404, detail="No election results found for this period")
    return results

# Pop size ratios endpoint
@router.get("/pop-size-ratios/{period_id}", response_model=List[dict])
def get_pop_size_ratios(period_id: int, db: Session = Depends(get_session)):
    """
    Get pop size ratios for a specific period.
    Returns all pops with their pop_size and percentage of total population.
    """
    from sqlmodel import select, func
    
    # Verify period exists
    period = crud.get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    
    # Get all pop-periods for this period with pop details
    statement = select(PopPeriod, Pop).join(Pop, PopPeriod.pop_id == Pop.id).where(PopPeriod.period_id == period_id)
    results = db.exec(statement).all()
    
    if not results:
        return []
    
    # Calculate total population and ratios
    total_population = sum(pop_period.pop_size for pop_period, _ in results)
    
    pop_ratios = []
    for pop_period, pop in results:
        percentage = (pop_period.pop_size / total_population * 100) if total_population > 0 else 0
        pop_ratios.append({
            'pop_name': pop.name,
            'pop_size': pop_period.pop_size,
            'percentage': round(percentage, 2)
        })
    
    # Sort by pop_size descending
    pop_ratios.sort(key=lambda x: x['pop_size'], reverse=True)
    
    return pop_ratios


@router.get("/simulation/period/{period_id}/pop-votes", response_model=List[PopVote])
def get_simulation_pop_votes(period_id: int, db: Session = Depends(get_session)):
    """Get all pop votes for a period."""
    votes = crud.get_items(db, PopVote, filters={"period_id": period_id})
    if not votes:
        raise HTTPException(status_code=404, detail="No pop votes found for this period")
    return votes


@router.get("/simulation/pop-period/{pop_period_id}/distance-scoring", response_model=List[Dict[str, Any]])
def get_pop_period_distance_scoring(pop_period_id: int, db: Session = Depends(get_session)):
    """Get distance scoring curve (0-100) for a specific PopPeriod."""
    # Get the PopPeriod entry
    pop_period = crud.get_item(db, PopPeriod, pop_period_id)
    if not pop_period:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    
    # Convert to dict for compatibility
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
    
    return get_distance_scoring_curve(pop_period_dict)