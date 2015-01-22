from utils import entity_resolver

resolver = entity_resolver.MasterEntitiesResolver()

test_entry = "Mr David Warburton"
test_type = "MP - Member of Parliament"
test_recipient = None


def parse_recipient(entry, entry_type, recipient_type):
    if entry_type == "MP - Member of Parliament":
        print "trying mp search"
        result = resolver.find_mp(entry)
    elif entry_type == "Political Party" or \
            recipient_type == "Political Party":
        result = resolver.find_party(entry)
    else:
        result = resolver.get_entities(entry)
        if result and isinstance(result, list):
            result = result[0]
    return result

print parse_recipient(test_entry, test_type, test_recipient)