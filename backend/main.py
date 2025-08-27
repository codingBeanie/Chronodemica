import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
from models import Period, Pop, PopPeriod, Party, PartyPeriod, PopVote, ElectionResult
from routers import router

# Load environment variables
load_dotenv()

app = FastAPI(title="Chronodemica Backend", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronodemica.db")
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