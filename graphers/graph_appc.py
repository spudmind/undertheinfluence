# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models.influencers_models import Lobbyist
from data_models.influencers_models import LobbyingClient
from data_models.influencers_models import LobbyRelationship
from data_models.influencers_models import LobbyEmployee


class GraphAppc():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "appc_parse"

    def run(self):
        self._logger.debug("\n\nGraphing APPC")
        all_lobbyists = self.db.fetch_all(self.COLLECTION_NAME, paged=False)
        for doc in all_lobbyists:
            name = doc["lobbyist"]["name"]
            self._logger.debug("\nLobby Firm: %s" % name)
            lobby_firm = Lobbyist(name)
            if not lobby_firm.exists:
                lobby_firm.create()
            lobby_props = {
                "contact_details": doc["lobbyist"]["contact_details"],
                "address": doc["lobbyist"]["address"],
                "data_source": "appc"
            }
            lobby_firm.set_lobbyist_details(lobby_props)
            self._create_clients(lobby_firm, doc["clients"], doc["meta"])
            self._create_staff(lobby_firm, doc["staff"], doc["meta"])

    def _create_clients(self, firm, clients, meta):
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
                relationship.update_raw_record(self.meta_to_text(meta))

    def _create_staff(self, firm, staff, meta):
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
                relationship.update_raw_record(self.meta_to_text(meta))

    def _create_relationship(self, firm, name, connection):
        props = {"lobbying_firm": firm, connection: name}
        relationship = u"{} and {}".format(firm, name)
        new_relationship = LobbyRelationship(relationship)
        if not new_relationship.exists:
            new_relationship.create()
        new_relationship.set_relationship_details(props)
        return new_relationship

    @staticmethod
    def meta_to_text(meta):
        text = u"""
            linked_from: {0}\nsource: {1}\nfetched: {2}\n
            date_from: {3}\ndate_to: {4}\n""".format(
            meta["linked_from"],
            meta["source"],
            meta["fetched"],
            meta["date_range"]["to"],
            meta["date_range"]["from"],
        )
        return text