import scraperwiki

#filename = "/home/warren/git/spud/scrapers/prca/store/agency_2014-09_2014-11.pdf"
filename = "/root/uti/scrapers/prca/store/agency_2010-12_2011-02.pdf"

with open(filename) as f:
    pdf_string = f.read()
# convert to xml
xml_string = scraperwiki.pdftoxml(pdf_string)
# parse xml
print "xml_string:", xml_string