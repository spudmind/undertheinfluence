# -*- coding: utf-8 -*-
import logging
import json
from utils import mongo
from data_models.influencers_models import LobbyAgency
from data_models.influencers_models import LobbyingClient
from data_models.influencers_models import LobbyRelationship
from data_models.influencers_models import LobbyEmployee


class GraphPrca():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.PREFIX = "prca"

    def run(self):
        self._logger.debug("\n\nGraphing PRCA")
        all_lobbyists = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_lobbyists:

            name = doc["name"]
            self._logger.debug("\nLobby Agency: %s" % name)

            lobby_firm = LobbyAgency(name)
            if not lobby_firm.exists:
                lobby_firm.create()

            lobby_props = {
                "pa_contact": doc["pa_contact"],
                "contact_details": doc["contact_details"]
            }
            lobby_firm.set_lobbyist_details(lobby_props)

            self.d = {
                "lobby_agency": doc["name"],
                "source_url": doc["source"]["url"],
                "source_linked_from": doc["source"]["linked_from_url"],
                "source_fetched": doc["source"]["fetched"],
                "meta": doc["meta"],
                "from_date": doc["date_range"][0],
                "to_date": doc["date_range"][1]
            }

            self._create_clients(lobby_firm, doc["clients"])
            self._create_staff(lobby_firm, doc["staff"])

    def _create_clients(self, firm, clients):
        if clients:
            for entry in clients:
                self._logger.debug("... client: %s" % entry)

                client = LobbyingClient(entry)
                if not client.exists:
                    client.create()
                client.set_client_details()

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
                self._logger.debug("... staff: %s" % entry)
                staff = LobbyEmployee(entry)
                if not staff.exists:
                    staff.create()
                staff.set_employee_details({"data_source": "prca"})
                relationship = self._create_relationship(
                    firm.name, staff.name, "employee"
                )
                relationship.link_firm(firm)
                relationship.link_staff(staff)
                relationship.set_from_date(self.d["from_date"])
                relationship.set_to_date(self.d["to_date"])

    def _create_relationship(self, firm, name, connection):
        props = {"lobbying_firm": firm, connection: name}
        relationship = u"{} and {}".format(firm, name)
        new_relationship = LobbyRelationship(relationship)
        if not new_relationship.exists:
            new_relationship.create()
        new_relationship.set_relationship_details(props)
        return new_relationship
