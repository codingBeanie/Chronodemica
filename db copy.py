from sqlmodel import SQLModel, create_engine, Session, desc, select
import os
from models import *
import logging
import streamlit as st
import pandas as pd

sqlite_file_name = "chronodemica.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)


###########################################################################
# Initialize
def init_db():
    if not os.path.exists(sqlite_file_name):
        SQLModel.metadata.create_all(engine)


############################################################################
# PERIOD Queries
def get_period_options():
    with Session(engine) as session:
        periods = session.exec(select(Period)).all()
        list_of_years = [period.year for period in periods]
        return list_of_years


def get_previous_period(year):
    with Session(engine) as session:
        previous_period = (
            session.query(Period)
            .filter(Period.year < year)
            .order_by(desc(Period.year))
            .first()
        )
        return previous_period.year if previous_period else None


############################################################################
# Detailed Queries
def get_detailed_data(model, year):
    pass


############################################################################
# District Queries
def get_valid_districts(year):
    with Session(engine) as session:
        districts = session.exec(
            select(District)
            .filter(
                (
                    (District.valid_from_year <= year)
                    | District.valid_from_year.is_(None)
                )
                & (
                    (District.valid_to_year.is_(None))
                    | (District.valid_to_year >= year)
                )
            )
            .order_by(District.name)
        ).all()
        return districts


def get_district_population(district_name, period_year):
    with Session(engine) as session:
        # get ids for district and period
        district = (
            session.query(District).filter(District.name == district_name).first()
        )
        period = session.query(Period).filter(Period.year == period_year).first()
        if not district or not period:
            return 0

        # get the total population for the district in the given period
        district_periods = (
            session.query(DistrictPeriod)
            .filter(
                DistrictPeriod.district_id == district.id,
                DistrictPeriod.period_id == period.id,
            )
            .all()
        )
        if not district_periods:
            return 0
        else:
            sum_population = sum(
                dp.total_population
                for dp in district_periods
                if dp.total_population is not None
            )
            return sum_population


def get_district_period_data(district_name, period_year):
    default_population = 1000
    default_ratio = 0.7

    with Session(engine) as session:
        # get ids for district and period
        district = session.exec(
            select(District).filter(District.name == district_name)
        ).first()
        period = session.exec(select(Period).filter(Period.year == period_year)).first()
        if not district or not period:
            return None

        valid_districts = get_valid_districts(period_year)
        # check if district is valid for period
        if district not in valid_districts:
            return None

        # get all valid pops for the period
        pops = get_valid_pops(period_year)
        pop_dict = {pop.id: pop for pop in pops}
        pop_ids = [pop.id for pop in pops]

        # check if data is already present, else create it
        for pop_id in pop_ids:
            district_period = session.exec(
                select(DistrictPeriod).filter(
                    DistrictPeriod.district_id == district.id,
                    DistrictPeriod.period_id == period.id,
                    DistrictPeriod.pop_id == pop_id,
                )
            ).first()
            if not district_period:
                # for reference, try to find the previous period's data
                previous_period = session.exec(
                    select(Period)
                    .filter(Period.year < period.year)
                    .order_by(Period.year.desc())
                ).first()

                if previous_period:
                    # there is at least one previous period, but maybe no data for it
                    previous_data = session.exec(
                        select(Period).filter(
                            DistrictPeriod.district_id == district.id,
                            DistrictPeriod.period_id == previous_period.id,
                            DistrictPeriod.pop_id == pop_id,
                        )
                    ).first()
                    if previous_data:
                        # there is data as a reference, use it
                        session.add(
                            DistrictPeriod(
                                district_id=district.id,
                                period_id=period.id,
                                pop_id=pop_id,
                                total_population=previous_data.total_population,
                                ratio_eligible=previous_data.ratio_eligible,
                            )
                        )
                        session.commit()
                    else:
                        # no previous data, no reference, create new
                        session.add(
                            DistrictPeriod(
                                district_id=district.id,
                                period_id=period.id,
                                pop_id=pop_id,
                                total_population=default_population,
                                ratio_eligible=default_ratio,
                            )
                        )
                        session.commit()
                else:
                    # create new entry with default values
                    session.add(
                        DistrictPeriod(
                            district_id=district.id,
                            period_id=period.id,
                            pop_id=pop_id,
                            total_population=default_population,
                            ratio_eligible=default_ratio,
                        )
                    )
                    session.commit()

        # query again to get the data
        district_period_data = session.exec(
            select(DistrictPeriod)
            .filter(
                DistrictPeriod.district_id == district.id,
                DistrictPeriod.period_id == period.id,
            )
            .order_by(desc(DistrictPeriod.total_population))
        ).all()
        # add district and period names to the data
        district_period_data = [
            {
                "district": district.name,
                "district_id": district.id,
                "period": period.year,
                "period_id": period.id,
                "pop_id": district_data.pop_id,
                "pop_name": pop_dict.get(district_data.pop_id).name,
                "total_population": district_data.total_population,
                "ratio_eligible": district_data.ratio_eligible,
            }
            for district_data in district_period_data
        ]
        return district_period_data


def save_district_period_data(district_name=None, period_year=None, pop_name=None):
    with Session(engine) as session:
        # get ids for district and period
        district = (
            session.query(District).filter(District.name == district_name).first()
        )
        period = session.query(Period).filter(Period.year == period_year).first()
        pop = session.query(Pop).filter(Pop.name == pop_name).first()
        population = st.session_state.get(f"total_population_{pop.name}")
        ratio_eligible = st.session_state.get(f"ratio_eligible_{pop.name}")
        # print(f"District: {district}, Period: {period}, Pop: {pop}, Population: {population}, Ratio Eligible: {ratio_eligible}")
        if not district or not period or not pop:
            return False

        # update or create the DistrictPeriod entry
        district_period = (
            session.query(DistrictPeriod)
            .filter(
                DistrictPeriod.district_id == district.id,
                DistrictPeriod.period_id == period.id,
                DistrictPeriod.pop_id == pop.id,
            )
            .first()
        )

        if district_period:
            # update existing entry
            district_period.total_population = population
            district_period.ratio_eligible = ratio_eligible
        else:
            # create new entry
            district_period = DistrictPeriod(
                district_id=district.id,
                period_id=period.id,
                pop_id=pop.id,
                total_population=population,
                ratio_eligible=ratio_eligible,
            )
            session.add(district_period)

        session.commit()
        return True


############################################################################
# Population Queries
def get_valid_pops(year):
    with Session(engine) as session:
        pops = (
            session.query(Pop)
            .filter(
                ((Pop.valid_from_year <= year) | Pop.valid_from_year.is_(None))
                & ((Pop.valid_to_year.is_(None)) | (Pop.valid_to_year >= year))
            )
            .order_by(Pop.name)
            .all()
        )
        return pops


def get_pop_period_data(pop_name, period_year):
    default_social_orientation = 0.0
    default_economic_orientation = 0.0
    default_max_political_distance = 0.5
    default_ratio_voting = 0.8

    with Session(engine) as session:
        # get ids for pop and period
        pop = session.query(Pop).filter(Pop.name == pop_name).first()
        period = session.query(Period).filter(Period.year == period_year).first()
        valid_pops = get_valid_pops(period_year)

        # check if pop is valid for period
        if pop not in valid_pops:
            return None

        # Try to get the PopPeriod data
        pop_period = (
            session.query(PopPeriod)
            .filter(PopPeriod.pop_id == pop.id, PopPeriod.period_id == period.id)
            .first()
        )

        # check if data is already present, else create it
        if pop_period is None:
            # for reference, try to find the previous period's data
            previous_period = (
                session.query(Period)
                .filter(Period.year < period.year)
                .order_by(Period.year.desc())
                .first()
            )

            if previous_period:
                # there is at least one previous period, but maybe no data for it
                previous_data = (
                    session.query(PopPeriod)
                    .filter(
                        PopPeriod.pop_id == pop.id,
                        PopPeriod.period_id == previous_period.id,
                    )
                    .first()
                )
                if previous_data:
                    # there is data as a reference, use it
                    session.add(
                        PopPeriod(
                            pop_id=pop.id,
                            period_id=period.id,
                            social_orientation=previous_data.social_orientation,
                            economic_orientation=previous_data.economic_orientation,
                            max_politcal_distance=previous_data.max_politcal_distance,
                            ratio_voting=previous_data.ratio_voting,
                        )
                    )
                    session.commit()
                else:
                    # no previous data, no reference, create new
                    session.add(
                        PopPeriod(
                            pop_id=pop.id,
                            period_id=period.id,
                            social_orientation=default_social_orientation,
                            economic_orientation=default_economic_orientation,
                            max_politcal_distance=default_max_political_distance,
                            ratio_voting=default_ratio_voting,
                        )
                    )
                    session.commit()
            else:
                # create new entry with default values
                session.add(
                    PopPeriod(
                        pop_id=pop.id,
                        period_id=period.id,
                        social_orientation=default_social_orientation,
                        economic_orientation=default_economic_orientation,
                        max_politcal_distance=default_max_political_distance,
                        ratio_voting=default_ratio_voting,
                    )
                )
                session.commit()
        # query again to get the data
        pop_period_data = (
            session.query(PopPeriod)
            .filter(PopPeriod.pop_id == pop.id, PopPeriod.period_id == period.id)
            .first()
        )
        return pop_period_data


def save_pop_period_data(pop_name=None, period_year=None):
    with Session(engine) as session:
        # get ids for pop and period
        pop = session.exec(select(Pop).filter(Pop.name == pop_name)).first()
        period = session.exec(select(Period).filter(Period.year == period_year)).first()
        social_orientation = st.session_state.get(f"social_orientation_{pop.name}")
        economic_orientation = st.session_state.get(f"economic_orientation_{pop.name}")
        max_political_distance = st.session_state.get(
            f"max_political_distance_{pop.name}"
        )
        ratio_voting = st.session_state.get(f"ratio_voting_{pop.name}")

        if not pop or not period:
            return False

        # update or create the PopPeriod entry
        pop_period = session.exec(
            select(PopPeriod).filter(
                PopPeriod.pop_id == pop.id, PopPeriod.period_id == period.id
            )
        ).first()

        if pop_period:
            # update existing entry
            pop_period.social_orientation = social_orientation
            pop_period.economic_orientation = economic_orientation
            pop_period.max_politcal_distance = max_political_distance
            pop_period.ratio_voting = ratio_voting
        else:
            # create new entry
            pop_period = PopPeriod(
                pop_id=pop.id,
                period_id=period.id,
                social_orientation=social_orientation,
                economic_orientation=economic_orientation,
                max_politcal_distance=max_political_distance,
                ratio_voting=ratio_voting,
            )
            session.add(pop_period)

        session.commit()
        return True


############################################################################
# Party
def get_valid_parties(year):
    with Session(engine) as session:
        parties = session.exec(
            select(Party)
            .filter(
                ((Party.valid_from_year <= year) | Party.valid_from_year.is_(None))
                & ((Party.valid_to_year.is_(None)) | (Party.valid_to_year >= year))
            )
            .order_by(Party.short_name)
        ).all()
        return parties


def get_party_period_data(party_short_name, period_year):
    default_social_orientation = 0.0
    default_economic_orientation = 0.0
    default_political_strength = 0.5

    with Session(engine) as session:
        # get ids for party and period
        party = session.exec(
            select(Party).filter(Party.short_name == party_short_name)
        ).first()
        period = session.exec(select(Period).filter(Period.year == period_year)).first()
        valid_parties = get_valid_parties(period_year)

        # check if party is valid for period
        if party not in valid_parties:
            return None

        # Try to get the PartyPeriod data
        party_period = session.exec(
            select(PartyPeriod).filter(
                PartyPeriod.party_id == party.id, PartyPeriod.period_id == period.id
            )
        ).first()

        # check if data is already present, else create it
        if party_period is None:
            # for reference, try to find the previous period's data
            previous_period = session.exec(
                select(Period)
                .filter(Period.year < period.year)
                .order_by(desc(Period.year))
            ).first()

            if previous_period:
                # there is at least one previous period, but maybe no data for it
                previous_data = session.exec(
                    select(PartyPeriod).filter(
                        PartyPeriod.party_id == party.id,
                        PartyPeriod.period_id == previous_period.id,
                    )
                ).first()
                if previous_data:
                    # there is data as a reference, use it
                    session.add(
                        PartyPeriod(
                            party_id=party.id,
                            period_id=period.id,
                            social_orientation=previous_data.social_orientation,
                            economic_orientation=previous_data.economic_orientation,
                            political_strength=previous_data.political_strength,
                        )
                    )

                    session.commit()
                else:
                    # no previous data, no reference, create new
                    session.add(
                        PartyPeriod(
                            party_id=party.id,
                            period_id=period.id,
                            social_orientation=default_social_orientation,
                            economic_orientation=default_economic_orientation,
                            political_strength=default_political_strength,
                        )
                    )
                    session.commit()
            else:
                # create new entry with default values
                session.add(
                    PartyPeriod(
                        party_id=party.id,
                        period_id=period.id,
                        social_orientation=default_social_orientation,
                        economic_orientation=default_economic_orientation,
                        political_strength=default_political_strength,
                    )
                )
                session.commit()

        # query again to get the data
        party_period_data = session.exec(
            select(PartyPeriod).filter(
                PartyPeriod.party_id == party.id, PartyPeriod.period_id == period.id
            )
        ).first()
        return party_period_data


def save_party_period_data(party_short_name=None, period_year=None):
    with Session(engine) as session:
        # get ids for party and period
        party = session.exec(
            select(Party).filter(Party.short_name == party_short_name)
        ).first()
        period = session.exec(select(Period).filter(Period.year == period_year)).first()
        social_orientation = st.session_state.get(
            f"social_orientation_party_{party.id}"
        )
        economic_orientation = st.session_state.get(
            f"economic_orientation_party_{party.id}"
        )
        political_strength = st.session_state.get(
            f"political_strength_party_{party.id}"
        )

        if not party or not period:
            return False

        # update or create the PartyPeriod entry
        party_period = session.exec(
            select(PartyPeriod).filter(
                PartyPeriod.party_id == party.id, PartyPeriod.period_id == period.id
            )
        ).first()

        if party_period:
            # update existing entry
            party_period.social_orientation = social_orientation
            party_period.economic_orientation = economic_orientation
            party_period.political_strength = political_strength
        else:
            # create new entry
            party_period = PartyPeriod(
                party_id=party.id,
                period_id=period.id,
                social_orientation=social_orientation,
                economic_orientation=economic_orientation,
                political_strength=political_strength,
            )
            session.add(party_period)

        session.commit()


############################################################################
# Statistics Queries
def get_total_population(period_year):
    with Session(engine) as session:
        period = session.query(Period).filter(Period.year == period_year).first()
        if not period:
            return 0
        districtPeriods = (
            session.query(DistrictPeriod)
            .filter(DistrictPeriod.period_id == period.id)
            .all()
        )
        return sum(
            dp.total_population
            for dp in districtPeriods
            if dp.total_population is not None
        )


def get_politcal_compass_parties(period_year):
    with Session(engine) as session:
        period = session.exec(select(Period).filter(Period.year == period_year)).first()
        if not period:
            return None

        party_periods = session.exec(
            select(PartyPeriod).filter(PartyPeriod.period_id == period.id)
        ).all()

        parties = []
        for party in party_periods:
            party_obj = session.exec(
                select(Party).filter(Party.id == party.party_id)
            ).first()
            party_data = {
                "full_name": party_obj.full_name,
                "short_name": party_obj.short_name,
                "social_orientation": party.social_orientation,
                "economic_orientation": party.economic_orientation,
                "political_strength": party.political_strength,
            }
            parties.append(party_data)

        return parties
