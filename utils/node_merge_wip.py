from data_models.core import Utility, NamedEntity


source = "89715"
#target = "Chris Huhne"
target = "37217"


def merge(source_name=None, source_id=None, target_name=None, target_id=None):
    to_copy = None
    if source_name:
        print "source_node", source_name
        to_copy = Utility(name=source_name)
    if source_id:
        name = Utility(node_id=source_id).vertex["name"]
        to_copy = Utility(name=name)

    labels = to_copy.get_labels()
    properties = to_copy.get_properties()
    rels = to_copy.get_relationships()

    print "target_node", target_name
    the_target = Utility(target_name)
    if target_name:
        print "target_node", target_name
        the_target = Utility(name=target_name)
    if target_id:
        name = Utility(node_id=target_id).vertex["name"]
        the_target = Utility(name=name)

    if 'name' in properties:
        del properties['name']
    print "\nlabels to copy", labels
    print "\nproperties to copy", properties
    print "\nrels to copy", rels

    the_target.set_node_properties(
        labels=labels,
        properties=properties
    )
    the_target.connect_to_ids(rels)

    post = Utility(target_name)
    print '*** POST ***'
    if post.exists:
        print post.get_labels()
        print post.get_properties()
        print post.get_relationships()
    print "\n"

    # to_copy.delete()

merge(source_id=source, target_id=target)
