import streamlit as st
from db import *
from models import *
from simulation import *
import pandas as pd
import itertools


class Coalitions:
    def __init__(self, period_id):
        self.period_id = period_id
        self.df_coalitions = None

        # Get Election Results
        self.election_results = get_entries(ElectionResult, {"period_id": period_id})
        # filter in_parliament
        self.parliament = [
            result
            for result in self.election_results
            if result["in_parliament"] is True
        ]
        # Enrich data
        for entry in self.parliament:
            party = get_entries(Party, {"id": entry["party_id"]})[0]
            party_period = get_entries(
                PartyPeriod, {"party_id": entry["party_id"], "period_id": period_id}
            )[0]
            entry["full_name"] = party["full_name"]
            entry["name"] = party["name"]
            entry["color"] = party["color"]
            entry["social_orientation"] = party_period["social_orientation"]
            entry["economic_orientation"] = party_period["economic_orientation"]

        # sort by most seats
        self.parliament.sort(key=lambda x: x["seats"], reverse=True)

        # Sum of seats
        self.total_seats = sum(entry["seats"] for entry in self.parliament)

        self.create_coalition_mapping()
        self.draw_coalition_table()

    def create_coalition_mapping(self):
        coalition_mapping = []
        party_combinations = []

        # Create all combinations of parties in parliament
        for r in range(2, len(self.parliament) + 1):
            party_combinations.extend(itertools.combinations(self.parliament, r))

        # Iterate through each combination and calculate coalition values
        for combination in party_combinations:
            total_seats = sum(party["seats"] for party in combination)
            has_majority = total_seats > (self.total_seats / 2)
            party_ids = [party["party_id"] for party in combination]
            party_names = [party["name"] for party in combination]
            party_fullnames = [party["full_name"] for party in combination]
            party_seats = [party["seats"] for party in combination]
            parties_in_government = [party["in_government"] for party in combination]

            # find all combinations within potential coalition
            party_combinations = list(itertools.combinations(party_ids, 2))
            distances = []

            for combination in party_combinations:
                party_1 = get_entries(
                    PartyPeriod,
                    {"period_id": self.period_id, "party_id": combination[0]},
                )[0]
                party_2 = get_entries(
                    PartyPeriod,
                    {"period_id": self.period_id, "party_id": combination[1]},
                )[0]
                distance = calculate_distance(
                    party_1["social_orientation"],
                    party_1["economic_orientation"],
                    party_2["social_orientation"],
                    party_2["economic_orientation"],
                    ratio=False,
                )
                distances.append(distance)

            # Calculate average distance
            total_distance = sum(distances)
            average_distance = (
                total_distance / len(party_combinations) if party_combinations else 0
            )

            # check if party is in government
            is_government = all(parties_in_government)

            coalition_data = {
                "party_ids": party_ids,
                "party_names": party_names,
                "party_fullnames": party_fullnames,
                "party_seats": party_seats,
                "total_seats": total_seats,
                "average_distance": average_distance,
                "total_distance": total_distance,
                "has_majority": has_majority,
                "is_government": is_government,
            }
            coalition_mapping.append(coalition_data)

        # Create DataFrame
        self.df_coalitions = pd.DataFrame(coalition_mapping)

        # filtering
        self.df_coalitions = self.df_coalitions[
            self.df_coalitions["has_majority"] == True
        ]
        # sorting
        self.df_coalitions = self.df_coalitions.sort_values(
            by="total_distance", ascending=True
        )

    def draw_coalition_table(self):
        with st.container(border=True):
            st.write("## Government & Coalitions")
            st.write("Combinations of parties that can form a government coalition.")

            total_parties = len(self.parliament)
            for data_row in self.df_coalitions.iterrows():
                with st.container(border=True):
                    coalition_option = data_row[1]

                    party_ids = coalition_option["party_ids"]
                    party_names = coalition_option["party_names"]
                    party_fullnames = coalition_option["party_fullnames"]
                    party_seats = coalition_option["party_seats"]
                    no_parties = len(party_names)
                    is_government = coalition_option["is_government"]

                    with st.container():
                        main_cols = st.columns([1, 7])
                        cols = main_cols[1].columns(total_parties)

                        if is_government:
                            main_cols[0].badge("Government Coalition", icon="🏛️")
                        else:
                            main_cols[0].button(
                                "Make Government",
                                icon="🤝",
                                key=f"coalition_{'_'.join(party_names)}",
                                use_container_width=True,
                                on_click=self.create_government_coalition,
                                args=(party_ids,),
                            )

                        # Coalition detail
                        for i in range(0, no_parties):
                            party_name = party_names[i]
                            party_fullname = party_fullnames[i]
                            party_seat = party_seats[i]
                            cols[i].write(f"**({party_name}) {party_fullname}**")
                            cols[i].write(f"_Seats: {party_seat}_")

    def create_government_coalition(self, party_ids):
        for entry in self.election_results:
            if entry["party_id"] in party_ids:
                update_entry(ElectionResult, entry["id"], {"in_government": True})
            else:
                update_entry(ElectionResult, entry["id"], {"in_government": False})
