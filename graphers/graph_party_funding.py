# -*- coding: utf-8 -*-
import logging
import json
from data_models.government_models import DonationRecipient
from data_models.influencers_models import Donor
from data_models.influencers_models import FundingRelationship
from data_models.influencers_models import RegisteredDonation
from utils import mongo
from data_models import government_models


class GraphPartyFunding():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.data_models = government_models
        self.db = mongo.MongoInterface()
        self.PREFIX = "party_funding"

    def run(self):
        all_donations = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_donations:

            name = doc["recipient"]
            donor = doc["donor_name"]

            recipient = self._get_recipient(name, doc)
            funding_relationship = self._create_relationship(name, donor)

            self.current = {
                "source_url": doc["source"]["url"],
                "source_linked_from": doc["source"]["linked_from_url"],
                "source_fetched": str(doc["source"]["fetched"]),
            }

            donor = self._get_donor(donor, doc)
            donation = self._create_donation(doc)

            recipient.link_funding_category(funding_relationship)
            funding_relationship.link_contributor(donor)
            funding_relationship.link_funding(donation)

    def _get_recipient(self, name, entry):
        new_recipient = DonationRecipient(name)
        if not new_recipient.exists:
            self._logger.debug("*not found*")
            new_recipient.create()

        props = {
            "recipient_type": entry["recipient_type"],
            "donee_type": entry["donee_type"],
            "data_source": "electoral_commission"
        }
        new_recipient.set_recipient_details(props)

        return new_recipient

    def _create_relationship(self, name, donor):
        category_name = u"{} and {}".format(donor, name)
        new_relationship = FundingRelationship(category_name)
        if not new_relationship.exists:
            new_relationship.create()

        props = {"recipient": name, "donor": donor}
        new_relationship.set_relationship_details(props)
        return new_relationship

    def _get_donor(self, name, entry):
        new_donor = Donor(name)
        if not new_donor.exists:
            new_donor.create()

        props = {
            "donor_type": entry["donor_type"],
            "company_reg": entry["company_reg"]
        }
        new_donor.set_donor_details(props)
        return new_donor

    def _create_donation(self, entry):
        if entry["received_date"] and len(entry["received_date"]) > 0:
            received_date = entry["received_date"]
        else:
            received_date = "Missing Received Date"
        summary = u"{} - {} - {} - {}".format(
            entry["recipient"],
            entry["donor_name"],
            received_date,
            entry["value"]
        )
        self._logger.debug(summary)
        new_donation = RegisteredDonation(summary)
        if not new_donation.exists:
            new_donation.create()

            props = {
                "recipient": entry["recipient"],
                "donor_name": entry["donor_name"],
                "amount": self.convert_to_number(entry["value"]),
                "ec_reference": entry["ec_reference"],
                "nature": entry["nature_provision"],
                "purpose": entry["purpose"],
                "recd_by": entry["recd_by"],
                "received_date": entry["received_date"],
                "reported_date": entry["reported_date"],
                "accepted_date": entry["accepted_date"],
                "6212": entry["6212"]
            }
            new_donation.set_donations_details(props)
            new_donation.set_donations_details(self.current)
            new_donation.set_dates(
                entry["received_date"],
                entry["reported_date"],
                entry["accepted_date"]
            )
        return new_donation

    @staticmethod
    def convert_to_number(amount):
        amount = amount.replace(u"£", u"")
        if ",00" == amount[-3:]:
            amount = amount.replace(",00", "")
        if "," in amount:
            amount = amount.replace(",", "")
        if "." in amount:
            amount = amount.split(".")[0]
        if amount.isdigit():
            return int(amount)
        else:
            return 0

