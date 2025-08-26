from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from models import Period, Pop, PopPeriod, Party, PartyPeriod, PopVote, ElectionResult
from routers import router

app = FastAPI(title="Chronodemica Backend", version="0.1.0")

# Database setup
DATABASE_URL = "sqlite:///./chronodemica.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Chronodemica Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}