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
            {"name": "CON", "full_name": "Conservative Party"},
            {"name": "LIB", "full_name": "Liberals"},
            {"name": "SDP", "full_name": "Socialist Democratic Party"},
            {"name": "COM", "full_name": "Communist Party"},
            {"name": "RWI", "full_name": "The Right Wing"},
        ]
        for party in party_data:
            new_party = Party(**party)
            session.add(new_party)
            session.commit()


###########################################################################
# CRUD Operations
# READ - General
def get_entries(model, filters=None, sort_by=None, descending=False):
    with Session(engine) as session:
        query = select(model)
        if filters:
            for key, value in filters.items():
                if "id" in key:
                    value = int(value)
                query = query.where(getattr(model, key) == value)
        if sort_by:
            column = getattr(model, sort_by)
            if descending:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(column)
        data = session.exec(query).all()
        result = [item.model_dump() for item in data]
        return result


# READ - Previous Periods
def get_previous_period(current_period_dict):
    with Session(engine) as session:
        query = (
            select(Period)
            .where(Period.year < current_period_dict["year"])
            .order_by(desc(Period.year))
            .limit(1)
        )
        result = session.exec(query).first()
        return result.model_dump() if result else None


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
    # print(f"Updating entry in {model.__name__} with ID {entry_id} and data {data}")
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
