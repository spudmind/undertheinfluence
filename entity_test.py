from data_models import government_models
from data_models.government_models import DonationRecipient
from utils import entity_resolver

resolver = entity_resolver.MasterEntitiesResolver()

#test_entry = "Lord na Lester"
test_entry = "The Rt Hon Vincent Cable MP"
test_type = "MP"
test_recipient = None


def parse_entities(entry):
    result = resolver.get_entities(entry)
    return result


def parse_recipient(entry, entry_type, recipient_type):
    print "Searching:", entry
    if entry_type == "MP":
        print "*trying mp search"
        result = resolver.find_mp(entry)
    elif entry_type == "Lord":
        print "*trying lord search"
        result = resolver.find_lord(entry)
    elif entry_type == "Political Party" or \
            recipient_type == "Political Party":
        print "*trying political party search"
        result = resolver.find_party(entry)
    else:
        print "*trying entity search"
        result = resolver.get_entities(entry)
        if result and isinstance(result, list):
            result = result[0]
    return result


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

print "found:", parse_recipient(test_entry, test_type, test_recipient)
print "found:", parse_entities(test_entry)
#node_properties_test()

