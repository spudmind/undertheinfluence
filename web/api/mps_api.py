from data_models import models


class MpsApi:
    def __init__(self):
        self.mps = models.MembersOfParliament()
        self.all = []
        self.government_members = []
        self.opposition_members = []

    def get_all(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.all

    def get_government(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.government_members

    def get_opposition(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.opposition_members

    def _fetch(self, page_size=20, skip_to=0):
        result = self.mps.get_all_mps(page_size, skip_to)
        for mp in result:
            shadow, government = False, False
            name, party, image = mp[0], mp[1], mp[2]
            mp_info = models.MemberOfParliament(name)
            positions = mp_info.positions
            departments = mp_info.departments
            mp_detail = {
                "name": name,
                "party": party,
                "image": image,
                "positions": positions,
                "departments": departments,
                "weight": mp[3]
            }
            self.all.append(mp_detail)
            for pos in positions:
                if "Shadow" in pos or party == "Labour":
                    shadow = True
                elif party in ['Liberal Democrat', 'Conservative']:
                    government = True
            if shadow:
                self.opposition_members.append(mp_detail)
            if government:
                self.government_members.append(mp_detail)
