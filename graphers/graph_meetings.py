# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import config
from data_models.influencers_models import MeetingAttendee
from data_models.government_models import GovernmentOffice
from data_models.government_models import GovernmentMeeting
from data_models.government_models import MemberOfParliament
from data_models.government_models import Lord


class GraphMeetings():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "meetings_parse"
        self.lords_titles = config.lords_titles

    def run(self):
        self._logger.info("\n\nGraphing Meetings")
        all_meetings = self.db.fetch_all(self.COLLECTION_NAME, paged=False)
        for doc in all_meetings:
            self._logger.debug("attendee:\t%s" % doc["organisation"])
            self._logger.debug("purpose:\t%s" % doc["purpose"])
            self._logger.debug("host_name:\t%s" % doc["host_name"])
            self._logger.debug("---\n")
            host = self._create_host(doc["host_name"])
            office = self._create_office(host, doc["host_position"])
            department = self._create_department(office, doc["department"])
            attendee = self._create_attendee(doc["organisation"])
            meeting = self._create_meeting(doc)
            meeting.link_participant(office)
            meeting.link_participant(attendee)

    def _create_host(self, name):
        if name:
            if any(title in name for title in self.lords_titles):
                politician = Lord(name)
                if not politician.exists:
                    politician.create()
                    politician.set_lord_details()
            else:
                politician = MemberOfParliament(name)
                if not politician.exists:
                    politician.create()
                    politician.set_mp_details()
            return politician
        return None

    def _create_office(self, host, office):
        new_office = GovernmentOffice(office)
        new_office.create()
        new_office.is_position(office_type="Ministerial Meeting")
        if host:
            host.link_position(new_office)
        return new_office

    def _create_department(self, office, department):
        new_dept = GovernmentOffice(department)
        new_dept.create()
        new_dept.is_department(office_type="Ministerial Meeting")
        office.link_department(new_dept)
        return new_dept

    def _create_attendee(self, name):
        new_attendee = MeetingAttendee(name)
        if not new_attendee.exists:
            new_attendee.create()
        new_attendee.set_attendee_details()
        return new_attendee

    def _create_meeting(self, meeting):
        meeting_title = u"{} - {} - {}".format(
            meeting["title"], meeting["organisation"], meeting["date"]
        )
        new_meeting = GovernmentMeeting(meeting_title)
        new_meeting.create()
        date = None
        if meeting["date"]:
            date = meeting["date"]
            new_meeting.set_meeting_date(date)
        props = {
            "host_name": meeting["host_name"],
            "host_position": meeting["host_position"],
            "department": meeting["department"],
            "title": meeting["title"],
            "attendee": meeting["organisation"],
            "purpose": meeting["purpose"],
            "date": date,
            "source_url": meeting["source"]["url"],
            "source_linked_from": meeting["source"]["linked_from_url"],
            "source_fetched": meeting["source"]["fetched"],
        }
        new_meeting.set_meeting_details(properties=props)
        return new_meeting