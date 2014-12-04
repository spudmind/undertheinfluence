from data_interfaces import mongo
from lxml import objectify
import os

categories = [
    "Directorships",
    "Remunerated employment, office, profession etc",
    "Clients",
    "Sponsorships",
    "Overseas visits",
    "Land and Property",
    "Shareholdings",
    "Miscellaneous"
]


def parse_xml(xml_path, file_name):
    with open(xml_path + file_name) as f:
            xml = f.read()
    root = objectify.fromstring(xml)
    for mp in root.getchildren():
        print mp.attrib["membername"]
        for category in mp.getchildren():
            if "name" in category.attrib:
                if category.attrib["name"] == "Remunerated employment, office, profession etc":
                    parse_category(category)
        print "\n---"


def parse_category(category):
    print "\t ", category.attrib["name"]
    for item in category.getchildren():
        print "\t\t", item.text


def parse():
    current_path = os.path.dirname(os.path.abspath(__file__))
    data = '/regmem'
    xml_data = current_path + data + "/"
    for f in os.listdir(xml_data):
        parse_xml(xml_data, f)