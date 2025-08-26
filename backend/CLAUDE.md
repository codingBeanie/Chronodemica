# Dokumentationen
Orientiere dich an die grundlegenden Dokumentationen:
FastAPI:https://fastapi.tiangolo.com
SQLModel:https://sqlmodel.tiangolo.com


# Datenmodelle
class Period(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    year: int = Field(unique=True)


class Pop(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class PopPeriod(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    pop_id: int = Field(foreign_key="pop.id")
    period_id: int = Field(foreign_key="period.id")
    population: int = Field(default=1000)
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    max_political_distance: int = Field(default=70)
    variety_tolerance: int = Field(default=50)
    non_voters_distance: int = Field(default=60)
    small_party_distance: int = Field(default=50)
    ratio_eligible: int = Field(default=75)


class Party(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    full_name: str | None
    color: str | None = Field(default="#525252")


class PartyPeriod(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="party.id")
    period_id: int = Field(foreign_key="period.id")
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    political_strength: int = Field(default=50)


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

# Struktur
* Fasse alle Models(-beschreibungen) in einer Datei zusammen.
* Versuche möglichst einheitliche, nicht redundante GET, POST, DELETE Funktionen zu schreiben. Versuche möglichst für alle Datenmodelle die gleichen Standard-Funktionen wie CRUD zu verwenden und keine eigenen Varianten zu erzuegen.

