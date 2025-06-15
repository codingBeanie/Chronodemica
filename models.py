from sqlmodel import SQLModel, Field
from typing import Optional


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
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    max_political_distance: int = Field(default=0)
    variety_tolerance: int = Field(default=0)
    non_voters_distance: int = Field(default=0)
    small_party_distance: int = Field(default=0)
    ratio_eligible: float = Field(default="0.7")


class Party(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    short_name: str = Field(unique=True)
    full_name: str | None


class PartyPeriod(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="party.id")
    period_id: int = Field(foreign_key="period.id")
    social_orientation: int = Field(default=0)
    economic_orientation: int = Field(default=0)
    political_strength: int = Field(default=50)
    color: str | None = Field(default="#525252")
