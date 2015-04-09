# -*- coding: utf-8 -*-
import logging
import json
from utils import mongo
from data_models.influencers_models import LobbyAgency
from data_models.influencers_models import LobbyingClient
from data_models.influencers_models import LobbyRelationship
from data_models.influencers_models import LobbyEmployee


class GraphAppc():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.PREFIX = "appc"

    def run(self):
        self._logger.debug("\n\nGraphing APPC")
        all_lobbyists = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_lobbyists:

            name = doc["name"]
            self._logger.debug("\nLobby Firm: %s" % name)

            lobby_firm = LobbyAgency(name)
            if not lobby_firm.exists:
                lobby_firm.create()

            lobby_props = {
                "contact_details": doc["contact_details"],
                "address": doc["address"]
            }
            lobby_firm.set_lobbyist_details(lobby_props)

            self.d = {
                "lobby_agency": doc["name"],
                "source_url": doc["source"]["url"],
                "source_linked_from": doc["source"]["linked_from_url"],
                "source_fetched": doc["source"]["fetched"],
                "from_date": doc["date_range"][0],
                "to_date": doc["date_range"][1]
            }

            self._create_clients(lobby_firm, doc["clients"])
            self._create_staff(lobby_firm, doc["staff"])

    def _create_clients(self, firm, clients):
        if clients:
            for entry in clients:
                self._logger.debug("... client: %s" % entry["name"])

                client = LobbyingClient(entry["name"])
                if not client.exists:
                    client.create()
                props = {
                    "description": entry["description"],
                    "data_source": "appc"
                }
                client.set_client_details(props)

                relationship = self._create_relationship(
                    firm.name, client.name, "client"
                )
                relationship.link_firm(firm)
                relationship.link_client(client)
                relationship.set_from_date(self.d["from_date"])
                relationship.set_to_date(self.d["to_date"])
                relationship.update_raw_record(json.dumps(self.d))

    def _create_staff(self, firm, staff):
        if staff:
            for entry in staff:
                self._logger.debug("... staff: %s" % entry["name"])

                staff = LobbyEmployee(entry["name"])
                if not staff.exists:
                    staff.create()
                props = {
                    "staff_type": entry["staff_type"],
                    "data_source": "appc"
                }
                staff.set_employee_details(props)

                relationship = self._create_relationship(
                    firm.name, staff.name, "employee"
                )
                relationship.link_firm(firm)
                relationship.link_staff(staff)
                relationship.set_from_date(self.d["from_date"])
                relationship.set_to_date(self.d["to_date"])
                relationship.update_raw_record(json.dumps(self.d))

    def _create_relationship(self, firm, name, connection):
        props = {"lobbying_firm": firm, connection: name}
        relationship = u"{} and {}".format(firm, name)
        new_relationship = LobbyRelationship(relationship)
        if not new_relationship.exists:
            new_relationship.create()
        new_relationship.set_relationship_details(props)
        return new_relationship