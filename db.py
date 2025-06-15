from sqlmodel import SQLModel, create_engine, Session, desc, select
import os
from models import *

sqlite_file_name = "chronodemica.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)


###########################################################################
# Initialize
def init_db():
    if not os.path.exists(sqlite_file_name):
        SQLModel.metadata.create_all(engine)
        create_demo_data()


def create_demo_data():
    with Session(engine) as session:
        # Periods
        period_data = [{"year": 2000}, {"year": 2004}]
        for period in period_data:
            new_period = Period(**period)
            session.add(new_period)
            session.commit()

        # Pops
        pop_data = [
            {"name": "Industry Workers"},
            {"name": "Farmers"},
            {"name": "Capitalists"},
            {"name": "Service Workers"},
        ]
        for pop in pop_data:
            new_pop = Pop(**pop)
            session.add(new_pop)
            session.commit()

        # Parties
        party_data = [
            {"short_name": "CON", "full_name": "Conservative Party"},
            {"short_name": "LIB", "full_name": "Liberals"},
            {"short_name": "SDP", "full_name": "Socialist Democratic Party"},
            {"short_name": "COM", "full_name": "Communist Party"},
            {"short_name": "RWI", "full_name": "The Right Wing"},
        ]
        for party in party_data:
            new_party = Party(**party)
            session.add(new_party)
            session.commit()


###########################################################################
# CRUD Operations
# READ - General
def get_entries(model, filters=None):
    with Session(engine) as session:
        query = select(model)
        if filters:
            for key, value in filters.items():
                query = query.where(getattr(model, key) == value)
        data = session.exec(query).all()
        result = [data.dict() for data in data]
        return result


# Create
def create_new_entry(model, data):
    with Session(engine) as session:
        new_entry = model(**data)
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        return True


# Update
def update_entry(model, entry_id, data):
    entry_id = int(entry_id)  # id from pd.dataframe is a numpy int, we need an int
    with Session(engine) as session:
        entry = session.exec(select(model).where(model.id == entry_id)).first()
        if entry:
            for key, value in data.items():
                setattr(entry, key, value)
            session.commit()
            session.refresh(entry)
            return True
        raise ValueError(f"Entry with ID {entry_id} not found in {model.__name__}")


# Delete
def delete_entry(model, entry_id):
    entry_id = int(entry_id)  # id from pd.dataframe is a numpy int, we need an int
    with Session(engine) as session:
        entry = session.exec(select(model).where(model.id == entry_id)).first()
        if entry:
            session.delete(entry)
            session.commit()
            return True
        raise ValueError(f"Entry with ID {entry_id} not found")


###########################################################################
