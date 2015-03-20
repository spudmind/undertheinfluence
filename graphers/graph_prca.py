# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models.influencers_models import LobbyAgency
from data_models.influencers_models import LobbyingClient
from data_models.influencers_models import LobbyRelationship
from data_models.influencers_models import LobbyEmployee


class GraphPrca():
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.db = mongo.MongoInterface()
        self._logger.debug("\n\nGraphing PRCA")
        all_lobbyists = self.db.fetch_all('prca_parse', paged=False)
        for doc in all_lobbyists:
            name = doc["lobbyist"]["name"]
            self._logger.debug("\nLobby Firm: %s" % name)
            lobby_firm = LobbyAgency(name)
            if not lobby_firm.exists:
                lobby_firm.create()
            lobby_props = {
                "pa_contact": doc["lobbyist"]["pa_contact"],
                "contact_details": doc["lobbyist"]["contact_details"],
                "data_source": "prca"
            }
            lobby_firm.set_lobbyist_details()
            self._create_clients(lobby_firm, doc["clients"], doc["meta"])
            self._create_staff(lobby_firm, doc["staff"], doc["meta"])

    def _create_clients(self, firm, clients, meta):
        if clients:
            for entry in clients:
                self._logger.debug("... client: %s" % entry)
                client = LobbyingClient(entry)
                if not client.exists:
                    client.create()
                client.set_client_details({"data_source": "prca"})
                relationship = self._create_relationship(
                    firm.name, client.name, "client"
                )
                relationship.link_firm(firm)
                relationship.link_client(client)
                relationship.update_raw_record(self.meta_to_text(meta))

    def _create_staff(self, firm, staff, meta):
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
            linked_from: {0}\nurl: {1}\npage: {2}\nfetched: {3}\n
            date_from: {4}\ndate_to: {5}\n""".format(
            meta["linked_from"],
            meta["url"],
            meta["page"],
            meta["fetched"],
            meta["date_range"]["to"],
            meta["date_range"]["from"],
        )
        return text