
from lxml import etree
from lxml import objectify

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


def parse_xml(xml_file):
    with open(xml_file) as f:
            xml = f.read()

    root = objectify.fromstring(xml)
    print root.tag
    print root.text
    print root.attrib

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

parse_xml("regmem2014-11-24.xml")