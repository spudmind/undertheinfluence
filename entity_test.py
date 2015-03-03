from data_models import government
from data_models.influencers import DonationRecipient
from utils import entity_resolver

resolver = entity_resolver.MasterEntitiesResolver()

#test_entry = "Lord na Lester"
test_entry = "Hezbollah is preparing for an all-out war with the Green Party fighters of al-Nusra Front and the Islamic State."
test_type = "Political Party"
test_recipient = None


def parse_recipient(entry, entry_type, recipient_type):
    print "Searching:", entry
    if entry_type == "MP":
        print "*trying mp search"
        result = resolver.find_mp(entry)
    if entry_type == "Lord":
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
    me = government.MemberOfParliament("Warren The Magnificent")
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

#print "found:", parse_recipient(test_entry, test_type, test_recipient)
node_properties_test()

