from data_models import government_models
from data_models.government_models import DonationRecipient
from utils import entity_resolver

resolver = entity_resolver.MasterEntitiesResolver()

#test_entry = "Lord na Lester"
#test_entry = "The Rt Hon Vincent Cable MP"
#test_entry = "Michael Denzil Xavier Portillo"
test_entry = "The Rt Hon Charles Kennedy MP"
test_type = "MP"
test_recipient = None


def parse_entities(entry):
    result = resolver.get_entities(entry)
    return result


def parse_recipient(entry):
    print "*trying mp search:", resolver.find_mp(entry)
    print "*trying lord search:", resolver.find_lord(entry)
    print "*trying party search:", resolver.find_party(entry)
    print "*trying entity search:", resolver.get_entities(entry)


def node_properties_test():
    me = government_models.MemberOfParliament("Warren The Magnificent")
    details = {
        "first_name": "Warren",
        "last_name": "The Magnificent",
        "party": "All the time",
        "twfy_id": "666",
        "number_of_terms": "infinite",
        # TODO change mp["guardian_image"] to mp["image_url"]
        "image_url": "http://ahyeah.com"
    }
    me.create()
    me.set_mp_details(details)
    new_me = DonationRecipient("Warren The Magnificent")
    extra_details = {
        "extra_indigo": "flatbush zombie"
    }
    new_me.set_recipient_details(extra_details)

parse_recipient(test_entry)
#print "found:", parse_entities(test_entry)
#node_properties_test()

