from data_interfaces import mongo
from lxml import objectify
import os

cache = mongo.MongoInterface()


def parse_xml(xml_path, file_name):
    with open(xml_path + file_name) as f:
            xml = f.read()
    root = objectify.fromstring(xml)
    contents = []
    for mp in root.getchildren():
        print mp.attrib["membername"]
        categories = []
        for category in mp.getchildren():
            if "name" in category.attrib:
                if "." in category.attrib["name"]:
                    category_name = category.attrib["name"].replace(".", "_")
                else:
                    category_name = category.attrib["name"]
                cat_data = {category_name: parse_category(category)}
                categories.append(cat_data)
        print "\n---"
        mp_data = {mp.attrib["membername"]: categories}
        contents.append(mp_data)
    file_name = file_name.split(".")[0]
    data = {file_name: contents}
    cache.db.mps_interests.save(data)


def parse_category(category):
    print "\t ", category.attrib["name"]
    items = []
    for item in category.getchildren():
        if item.getchildren():
            text = parse_item(item)
            items.append(text)
        else:
            text = item.text
            items.append(text)
        print "\t\t", text
    return items


def parse_item(items):
    string = ""
    for x in items.getchildren():
        if x.getchildren():
            for y in x.getchildren():
                if y.text is not None:
                    string += y.text
        else:
            if x.text is not None:
                string += x.text
    return string.strip()


def parse():
    current_path = os.path.dirname(os.path.abspath(__file__))
    data = '/regmem'
    xml_data = current_path + data + "/"
    for f in os.listdir(xml_data):
        parse_xml(xml_data, f)