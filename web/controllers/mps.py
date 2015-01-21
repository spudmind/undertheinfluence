from data_models import core, models


class MpAggregateController:
    def __init__(self):
        self.mps = models.MembersOfParliament()
        self.data_model = core.DataModel()
        self.government_members = []
        self.opposition_members = []
        self._set_properties()

    def government(self):
        for mp, weight in self.government_members:
            yield mp, weight

    def opposition(self):
        for mp, weight in self.opposition_members:
            yield mp, weight

    def _set_properties(self):
        for mp in self.mps.get_all_mps(page_size=20, skip_to=0):
            shadow, government = False, False
            mp, party, image, weight = mp[0], mp[1], mp[2], mp[3]
            mp_detail = models.MemberOfParliament(mp)
            positions = mp_detail.positions
            departments = mp_detail.departments
            aggregate_detail = {
                "name": mp,
                "party": party,
                "image": image,
                "positions": positions,
                "departments": departments
            }
            for pos in positions:
                if "Shadow" in pos or party == "Labour":
                    shadow = True
                elif party in ['Liberal Democrat', 'Conservative']:
                    government = True
            if shadow:
                self.opposition_members.append((aggregate_detail, weight))
            if government:
                self.government_members.append((aggregate_detail, weight))
