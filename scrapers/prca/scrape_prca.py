# -*- coding: utf-8 -*-
import logging
import re
from os import listdir
import os.path
from utils import mongo, pdftoxml


class ScrapePRCA():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        # prefix for database tables
<<<<<<< HEAD
        self.PREFIX = "prca"
=======
        self.prefix = "prca"
>>>>>>> 59-prca-parse
        # directory where files are stored
        self.STORE_DIR = "store"
        # the y-position of the top of the footer
        # (where the page number lives)
        self.FOOTER_Y = 1170
        self.CATEGORIES = {
            "contact": re.compile(r"^Office\(?s", re.IGNORECASE),
            "pa_contact": re.compile(r"CONTACT FOR PUBLIC AFFAIRS"),
            "staff": re.compile(r"(?:Employees|Staff).*? (?:performing|providing|conducted).*? (?:public affairs|PA|lobbying).*? (?:services|work)", re.IGNORECASE),
            "clients": re.compile(r"Clients for whom.*? (?:public affairs|lobbying)", re.IGNORECASE),
        }
        # self.CONTACT_CATS = {
        #     "Tel: ": "phone",
        #     "Fax: ": "fax",
        #     "Web: ": "website",
        # }

    # Various hacks due to pdf-related problems
    def pdf_hacks(self, blocks, filename, page_num):
        if filename.endswith("agency_2014-03_2014-05.pdf") and page_num == 20:
            return blocks[15:]
        if filename.endswith("agency_2014-06_2014-08.pdf") and page_num == 22:
            return blocks[25:]
        if filename.endswith("in-house_2014-03_2014-05.pdf") and page_num == 20:
            return blocks[18:]
        if filename.endswith("in-house_2014-06_2014-08.pdf") and page_num == 20:
            return blocks[18:]
        return blocks

    # Patch some errors in the PDFs, where the incorrect heading
    # has been used.
    def apply_patches(self, all_blocks, idx):
        if all_blocks[idx][0] == "The Communication Group plc.":
            all_blocks[idx+1] = (u"Office(s) address:", all_blocks[idx+1][1])
        elif all_blocks[idx][0] == "Email: cmclauchlin@webershandwick.com":
            all_blocks[idx+1] = (u"List of employees that have conducted lobbying services:", all_blocks[idx+1][1])
        return all_blocks

    def scrape_blocks_from_pdf(self, filename):
        self._logger.info("parsing: %s" % filename)
        # convert to xml
        pdf = pdftoxml.from_file(filename)
        all_blocks = []
        for page_num in range(1, pdf.page_count() + 1):
            # fetch a specific page of the document

            # fetch all text blocks on that page
            blocks = pdf.get_page(page_num)
            blocks = self.pdf_hacks(blocks, filename, page_num)

            # sort according to vertical position on page
            sorted_blocks = sorted(blocks, key=lambda x: x[1]["top"])

            # throw away the page number block
            if len(sorted_blocks) > 0 and sorted_blocks[-1][0] == str(page_num):
                # we check the thing we're removing is at
                # the bottom of the page
                assert(sorted_blocks[-1][1]["top"] > self.FOOTER_Y)
                sorted_blocks = sorted_blocks[:-1]

            # include the current page number with every block
            numbered_sorted_blocks = [(x[0], dict(x[1].items() + [("page", page_num)])) for x in sorted_blocks]

            # append the current page of blocks
            all_blocks += numbered_sorted_blocks
        return all_blocks

    def is_category(self, text):
        for k, regex in self.CATEGORIES.items():
            if regex.search(text) is not None:
                return k
        return False

    def blocks_to_agencies(self, all_blocks):
        agencies = []
        agency = None
        current_cat = None
        while self.CATEGORIES["contact"].match(all_blocks[1][0]) is None:
            # Remove initial blocks e.g. the title
            _ = all_blocks.pop(0)

        for idx, block in enumerate(all_blocks):
            all_blocks = self.apply_patches(all_blocks, idx)
            category = self.is_category(block[0])
            if (idx + 1) < len(all_blocks) and self.CATEGORIES["contact"].match(all_blocks[idx + 1][0]) is not None:
                # the following block is contact-related, so we've just finished
                # an agency and need to start a new one.
                #
                # add the completed agency to the list
                if agency is not None:
                    agencies.append(agency)

                # start a new agency
                agency = {"name": block[0], "meta": {"page": block[1]["page"]}}
            elif block[0] == "Declaration submitted by:":
                # [hack] this is just used in mixed_2009-12_2010-02.pdf
                current_cat = "ignore"
            elif category:
                current_cat = category
                # we shouldn't already have agency data for this category
                try:
                    assert(current_cat not in agency)
                except AssertionError:
                    print idx, block
                    print agency
                    raise
            # okay - if we've got to here, we're setting a property
            else:
                if current_cat not in agency:
                    agency[current_cat] = []
                agency[current_cat].append(block)
        if agency is not None:
            agencies.append(agency)
        return agencies

    def sort_agency_data(self, agencies):
        for agency in agencies:
            for cat in self.CATEGORIES.keys():
                if cat not in agency:
                    continue
                agency[cat] = sorted(agency[cat], key=lambda x: (x[1]["left"], x[1]["page"], x[1]["top"]))
                agency[cat] = [x[0] for x in agency[cat]]
        return agencies

    def save_to_db(self, agencies, meta):
        for agency in agencies:
            m = {k: v for k, v in meta.items() if k in ['linked_from', 'fetched', 'url']}
            agency["meta"] = dict(agency["meta"].items() + m.items())
            agency["date_from"] = meta["date_from"]
            agency["date_to"] = meta["date_to"]

            for k, v in agency.items():
                self._logger.debug("%s:      %s" % (k, v))
            self._logger.debug("---")

<<<<<<< HEAD
            agency_entity = self.db.save("%s_scrape" % self.PREFIX, agency)
=======
            agency_entity = self.db.save("%s_scrape" % self.prefix, agency)
>>>>>>> 59-prca-parse

    # # TODO! This is wrong at the moment
    # def parse_contact(self, agency):
    #     if "contact" not in agency:
    #         agency["contact"] = [{}]
    #     # attempt to parse contact info
    #     if value[:5] in self.CONTACT_CATS:
    #         key = self.CONTACT_CATS[value[:5]]
    #         value = value[5:]
    #         if key in agency["contact"][-1]:
    #             # we need to start a new contact
    #             agency["contact"].append({})
    #     else:
    #         key = "address"
    #     agency["contact"][-1][key] = value

    def parse_file(self, meta):
        filename = meta["filename"]
        current_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_path, self.STORE_DIR, filename)

        blocks = self.scrape_blocks_from_pdf(full_path)

        # Right - we have a big list of text blocks, roughly in order.
        # Now let's group them by agency.
        agencies = self.blocks_to_agencies(blocks)

        # We then re-sort - by section, then page, then horizontal position, then vertical position.
        # We do this because it matches the way the text is actually written - and that's
        # important because sometimes an entity (e.g. a company name) spans two pages.
        sorted_agencies = self.sort_agency_data(agencies)

        # TOOD: Extract the entities in the client and employee lists.
        # TODO: Save everything.
        self.save_to_db(sorted_agencies, meta)

    def run(self):
<<<<<<< HEAD
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
=======
        metas = self.db.fetch_all("%s_fetch" % self.prefix, paged=False)
>>>>>>> 59-prca-parse

        for meta in metas:
            if not meta["filename"].endswith(".pdf"):
                continue
            self.parse_file(meta)

def scrape():
    ScrapePRCA().run()
