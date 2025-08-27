import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
from models import (
    Period, Pop, PopPeriod, Party, PartyPeriod, 
    PopVote, ElectionResult
)
import crud

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronodemica.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

router = APIRouter()


# Period endpoints
@router.post("/periods/", response_model=Period)
def create_period(period: Period, db: Session = Depends(get_session)):
    return crud.create_item(db, period)

@router.get("/periods/", response_model=List[Period])
def read_periods(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, Period, skip, limit)

@router.get("/periods/{period_id}", response_model=Period)
def read_period(period_id: int, db: Session = Depends(get_session)):
    period = crud.get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period

@router.put("/periods/{period_id}", response_model=Period)
def update_period(period_id: int, period_update: dict, db: Session = Depends(get_session)):
    period = crud.get_item(db, Period, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return crud.update_item(db, period, period_update)

@router.delete("/periods/{period_id}", response_model=Period)
def delete_period(period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Period, period_id)


# Pop endpoints
@router.post("/pops/", response_model=Pop)
def create_pop(pop: Pop, db: Session = Depends(get_session)):
    return crud.create_item(db, pop)

@router.get("/pops/", response_model=List[Pop])
def read_pops(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, Pop, skip, limit)

@router.get("/pops/{pop_id}", response_model=Pop)
def read_pop(pop_id: int, db: Session = Depends(get_session)):
    pop = crud.get_item(db, Pop, pop_id)
    if not pop:
        raise HTTPException(status_code=404, detail="Pop not found")
    return pop

@router.put("/pops/{pop_id}", response_model=Pop)
def update_pop(pop_id: int, pop_update: dict, db: Session = Depends(get_session)):
    pop = crud.get_item(db, Pop, pop_id)
    if not pop:
        raise HTTPException(status_code=404, detail="Pop not found")
    return crud.update_item(db, pop, pop_update)

@router.delete("/pops/{pop_id}", response_model=Pop)
def delete_pop(pop_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Pop, pop_id)


# PopPeriod endpoints
@router.post("/pop-periods/", response_model=PopPeriod)
def create_pop_period(pop_period: PopPeriod, db: Session = Depends(get_session)):
    return crud.create_item(db, pop_period)

@router.get("/pop-periods/", response_model=List[PopPeriod])
def read_pop_periods(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, PopPeriod, skip, limit)

@router.get("/pop-periods/{pop_period_id}", response_model=PopPeriod)
def read_pop_period(pop_period_id: int, db: Session = Depends(get_session)):
    pop_period = crud.get_item(db, PopPeriod, pop_period_id)
    if not pop_period:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    return pop_period

@router.put("/pop-periods/{pop_period_id}", response_model=PopPeriod)
def update_pop_period(pop_period_id: int, pop_period_update: dict, db: Session = Depends(get_session)):
    pop_period = crud.get_item(db, PopPeriod, pop_period_id)
    if not pop_period:
        raise HTTPException(status_code=404, detail="PopPeriod not found")
    return crud.update_item(db, pop_period, pop_period_update)

@router.delete("/pop-periods/{pop_period_id}", response_model=PopPeriod)
def delete_pop_period(pop_period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PopPeriod, pop_period_id)


# Party endpoints
@router.post("/parties/", response_model=Party)
def create_party(party: Party, db: Session = Depends(get_session)):
    return crud.create_item(db, party)

@router.get("/parties/", response_model=List[Party])
def read_parties(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, Party, skip, limit)

@router.get("/parties/{party_id}", response_model=Party)
def read_party(party_id: int, db: Session = Depends(get_session)):
    party = crud.get_item(db, Party, party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@router.put("/parties/{party_id}", response_model=Party)
def update_party(party_id: int, party_update: dict, db: Session = Depends(get_session)):
    party = crud.get_item(db, Party, party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return crud.update_item(db, party, party_update)

@router.delete("/parties/{party_id}", response_model=Party)
def delete_party(party_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, Party, party_id)


# PartyPeriod endpoints
@router.post("/party-periods/", response_model=PartyPeriod)
def create_party_period(party_period: PartyPeriod, db: Session = Depends(get_session)):
    return crud.create_item(db, party_period)

@router.get("/party-periods/", response_model=List[PartyPeriod])
def read_party_periods(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, PartyPeriod, skip, limit)

@router.get("/party-periods/{party_period_id}", response_model=PartyPeriod)
def read_party_period(party_period_id: int, db: Session = Depends(get_session)):
    party_period = crud.get_item(db, PartyPeriod, party_period_id)
    if not party_period:
        raise HTTPException(status_code=404, detail="PartyPeriod not found")
    return party_period

@router.put("/party-periods/{party_period_id}", response_model=PartyPeriod)
def update_party_period(party_period_id: int, party_period_update: dict, db: Session = Depends(get_session)):
    party_period = crud.get_item(db, PartyPeriod, party_period_id)
    if not party_period:
        raise HTTPException(status_code=404, detail="PartyPeriod not found")
    return crud.update_item(db, party_period, party_period_update)

@router.delete("/party-periods/{party_period_id}", response_model=PartyPeriod)
def delete_party_period(party_period_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PartyPeriod, party_period_id)


# PopVote endpoints
@router.post("/pop-votes/", response_model=PopVote)
def create_pop_vote(pop_vote: PopVote, db: Session = Depends(get_session)):
    return crud.create_item(db, pop_vote)

@router.get("/pop-votes/", response_model=List[PopVote])
def read_pop_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, PopVote, skip, limit)

@router.get("/pop-votes/{pop_vote_id}", response_model=PopVote)
def read_pop_vote(pop_vote_id: int, db: Session = Depends(get_session)):
    pop_vote = crud.get_item(db, PopVote, pop_vote_id)
    if not pop_vote:
        raise HTTPException(status_code=404, detail="PopVote not found")
    return pop_vote

@router.put("/pop-votes/{pop_vote_id}", response_model=PopVote)
def update_pop_vote(pop_vote_id: int, pop_vote_update: dict, db: Session = Depends(get_session)):
    pop_vote = crud.get_item(db, PopVote, pop_vote_id)
    if not pop_vote:
        raise HTTPException(status_code=404, detail="PopVote not found")
    return crud.update_item(db, pop_vote, pop_vote_update)

@router.delete("/pop-votes/{pop_vote_id}", response_model=PopVote)
def delete_pop_vote(pop_vote_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, PopVote, pop_vote_id)


# ElectionResult endpoints
@router.post("/election-results/", response_model=ElectionResult)
def create_election_result(election_result: ElectionResult, db: Session = Depends(get_session)):
    return crud.create_item(db, election_result)

@router.get("/election-results/", response_model=List[ElectionResult])
def read_election_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud.get_items(db, ElectionResult, skip, limit)

@router.get("/election-results/{election_result_id}", response_model=ElectionResult)
def read_election_result(election_result_id: int, db: Session = Depends(get_session)):
    election_result = crud.get_item(db, ElectionResult, election_result_id)
    if not election_result:
        raise HTTPException(status_code=404, detail="ElectionResult not found")
    return election_result

@router.put("/election-results/{election_result_id}", response_model=ElectionResult)
def update_election_result(election_result_id: int, election_result_update: dict, db: Session = Depends(get_session)):
    election_result = crud.get_item(db, ElectionResult, election_result_id)
    if not election_result:
        raise HTTPException(status_code=404, detail="ElectionResult not found")
    return crud.update_item(db, election_result, election_result_update)

@router.delete("/election-results/{election_result_id}", response_model=ElectionResult)
def delete_election_result(election_result_id: int, db: Session = Depends(get_session)):
    return crud.delete_item(db, ElectionResult, election_result_id)