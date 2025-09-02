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
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    name: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    filters = {}
    if name is not None:
        filters["name"] = name
    return crud.get_items(db, Pop, skip, limit, filters, sort_by, sort_direction)

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
    skip: int = 0, 
    limit: int = 100, 
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    name: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    filters = {}
    if name is not None:
        filters["name"] = name
    return crud.get_items(db, Party, skip, limit, filters, sort_by, sort_direction)

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