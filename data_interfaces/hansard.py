from utils import theyworkforyou
import json


class TWFYHansard:
    def __init__(self, link=False):
        self.twfy = theyworkforyou.TWFY("ESHFQ9AQWgTuFyCfx7DAWpDc")

    def get_mps(self, **kwargs):
        return json.loads(
            self.twfy.api.getMPs(output="js", **kwargs)
        )

    def get_mp(self, person_id, **kwargs):
        return json.loads(
            self.twfy.api.getMP(output="js", id=person_id, **kwargs)
        )

    def get_mp_info(self, person_id, **kwargs):
        return json.loads(
            self.twfy.api.getMPInfo(output="js", id=person_id, **kwargs)
        )

    def get_lords(self, **kwargs):
        return json.loads(
            self.twfy.api.getLords(output="js", **kwargs)
        )

    def get_lord(self, person_id, **kwargs):
        return json.loads(
            self.twfy.api.getLord(output="js", id=person_id, **kwargs)
        )

    def get_mp_debates(self, debate_type, person, **kwargs):
        return json.loads(
            self.twfy.api.getDebates(output="js", type=debate_type, person=person, **kwargs)
        )

    def get_debate(self, debate_id):
        debate_found = self._get_debate_detail(
            "commons",
            debate_id
        )
        if debate_found:
            starting_point = debate_found[0]
            mp_comment = debate_found[-1]
            start = {
                    "date": starting_point["hdate"],
                    "content_count": starting_point["contentcount"],
                    "body": starting_point["body"],
                    "debate_id": starting_point["gid"]
            }
            mp_comment = {
                    "date": mp_comment["hdate"],
                    "body": mp_comment["body"],
                    "debate_id": mp_comment["gid"]
            }
            if len(debate_found) == 3:
                sub = debate_found[1]
                sub_cat = {
                    "date": sub["hdate"],
                    "body": sub["body"],
                    "content_count": sub["contentcount"],
                    "debate_id": sub["gid"]
                }
            else:
                sub_cat = None
            return start, sub_cat, mp_comment
        else:
            return None

    def get_full_debate(self, full_debate_id, sub_category=True):
        debate_full = self._get_debate_detail(
            "commons",
            full_debate_id
        )
        #print "\n\n[o] Getting Full Debate Details [id: %s count:%s]" \
        #      % (full_debate_id, len(debate_full))
        main = {
            "debate_id": debate_full[0]["gid"],
            "date": debate_full[0]["hdate"],
            "topic": debate_full[0]["body"]
        }
        if sub_category:
            sub_cat = {
                "debate_id": debate_full[1]["gid"],
                "date": debate_full[1]["hdate"],
                "topic": debate_full[1]["body"]
            }
            full_debate = debate_full[2:]
        else:
            sub_cat = None
            full_debate = debate_full[1:]
        return main, sub_cat, full_debate

    def _get_debate_detail(self, debate_type, debate_id, **kwargs):
        try:
            return json.loads(
                self.twfy.api.getDebates(output="js", type=debate_type, gid=debate_id, **kwargs)
            )
        except json.scanner.JSONDecodeError:
            print "JSONDecodeError"
            return None
