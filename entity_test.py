from utils import entity_resolver

resolver = entity_resolver.MasterEntitiesResolver()

test_entry = "Lord na Lester"
test_type = "Lord"
test_recipient = None


def parse_recipient(entry, entry_type, recipient_type):
    print "Searching for:", entry
    if entry_type == "MP":
        print "trying mp search"
        result = resolver.find_mp(entry)
    if entry_type == "Lord":
        print "trying lord search"
        result = resolver.find_lord(entry)
    elif entry_type == "Political Party" or \
            recipient_type == "Political Party":
        result = resolver.find_party(entry)
    else:
        result = resolver.get_entities(entry)
        if result and isinstance(result, list):
            result = result[0]
    return result

print parse_recipient(test_entry, test_type, test_recipient)