# Backend Architecture

## Documentation References
- FastAPI: https://fastapi.tiangolo.com
- SQLModel: https://sqlmodel.tiangolo.com

## Database Models (SQLModel/SQLAlchemy)

### Core Models
```python
class Period(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    year: int = Field(unique=True)

class Pop(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

class Party(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    full_name: str | None
    color: str | None = Field(default="#525252")
```

### Period-specific Models
```python
class PopPeriod(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    pop_id: int = Field(foreign_key="pop.id")
    period_id: int = Field(foreign_key="period.id")
    pop_size: int = Field(default=5)
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    max_political_distance: int = Field(default=70)
    variety_tolerance: int = Field(default=50)
    non_voters_distance: int = Field(default=60)
    small_party_distance: int = Field(default=50)
    ratio_eligible: int = Field(default=75)

class PartyPeriod(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="party.id")
    period_id: int = Field(foreign_key="period.id")
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    political_strength: int = Field(default=50)
```

### Result Models
```python
class PopVote(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    period_id: int = Field(foreign_key="period.id")
    pop_id: int = Field(foreign_key="pop.id")
    party_id: int = Field(foreign_key="party.id")
    votes: int = Field(default=0)

class ElectionResult(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    period_id: int = Field(foreign_key="period.id")
    party_id: int = Field(foreign_key="party.id")
    votes: int = Field(default=0)
    percentage: float = Field(default=0.0)
    seats: int = Field(default=0)
    in_parliament: bool = Field(default=False)
    in_government: bool = Field(default=False)
    head_of_government: bool = Field(default=False)
```

## API Structure & Patterns

### Centralized CRUD Operations
**MANDATORY:** Use standardized CRUD patterns for ALL models:

```python
# Standard endpoints for each model
@router.post("/", response_model=ModelType)
@router.get("/", response_model=List[ModelType]) 
@router.get("/{id}", response_model=ModelType)
@router.put("/{id}", response_model=ModelType)
@router.delete("/{id}", response_model=ModelType)
```

### Generic CRUD Functions
Create reusable CRUD operations in `/app/crud/`:
- **NO model-specific variations** unless absolutely necessary
- **Consistent error handling** across all endpoints
- **Unified response patterns** using FastAPI response models
- **Standard pagination** with skip/limit parameters

### Router Organization
- **One router per model** in `/app/routers/`
- **Consistent URL patterns**: `/api/v1/{model-name}/`
- **Uniform error responses** and status codes
- **Consolidated model imports** in single file

## Database Configuration
- **SQLite** for local development
- **Connection pooling** and proper session management
- **Database migrations** via Alembic if schema changes occur
- **Consistent table naming** and foreign key constraints

## Development Principles
- **Model consolidation** - all models in single file or organized module
- **CRUD standardization** - identical patterns across all models  
- **Error consistency** - uniform error handling and responses
- **Code reusability** - generic functions over specific implementations
- **Zero redundancy** - no duplicate CRUD logic between models