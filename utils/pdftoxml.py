# -*- coding: utf-8 -*-
from collections import defaultdict
import lxml.etree
import scraperwiki

'''
Wrapper around scraperwiki.pdftoxml. This file is
currently a mess of various different ideas, none
of which currently works.
'''


class PDFtoXML():
    def __init__(self, filename):
        # load the pdf
        with open(filename) as f:
            pdf_string = f.read()
        # convert to xml
        xml_string = scraperwiki.pdftoxml(pdf_string)
        # parse xml
        print "xml_string", xml_string
        self._xml = lxml.etree.fromstring(xml_string)
        self._pages = [self._page_to_blocks(page_num) for page_num in range(1, self.page_count() + 1)]

    def page_count(self):
        return len(self._xml.xpath('//page'))

    def get_page(self, page_num):
        if page_num < 1:
            raise IndexError("list index out of range")
        return self._pages[page_num - 1]

        # columns = {}
        # for x in blocks:
        #     l = x[1]["left"]
        #     if l not in columns:
        #         columns[l] = []
        #     columns[l].append(x[1]["top"])

        # column_pos = {pos: (min(tops), max(tops)) for pos, tops in columns.items() if len(tops) > 1}
        # col_locations = sorted(column_pos.keys())

        # blocks = sorted(blocks, key=lambda x: (x[1]["top"], x[1]["left"]))
        # rows = []
        # row_baseline = 0
        # for x in blocks:
        #     if x[1]["top"] > row_baseline:
        #         rows.append({})
        #         row_baseline = x[1]["top"]
        #     if x[1]["left"] in col_locations:
        #         idx = col_locations.index(x[1]["left"])
        #         rows[-1][idx] = x[0]
        #     else:

    # For a dict of dicts and some vertical value delta,
    # merge nearby rows together, returning a list of dicts
    def merge_nearby_rows(self, d, delta=7):
        prev = None
        n = []
        for x in sorted(d.keys()):
            if prev is not None and x-prev < delta:
                n[-1].update(d[x])
            else:
                n.append(d[x])
            prev = x
        return n

    # Sometimes a cell will spill onto multiple lines.
    # When this happens, we need to merge those lines
    # into a single row.
    def merge_continued_cells(self, l, min_cols=3):
        # this strictly merges up, and also happens to filter out
        # columns that didn't exist in the row above
        def merge_up(a, b):
            out = {}
            for k, v in a.items():
                if not b.get(k):
                    out[k] = v
                else:
                    new_str = "%s\n%s" % (v[0], b[k][0])
                    new_props = {
                        "left": min(b[k][1]["left"], v[1]["left"]),
                        "top": min(b[k][1]["top"], v[1]["top"]),
                    }
                    max_right = max(b[k][1]["left"] + b[k][1]["width"], v[1]["left"] + v[1]["width"])
                    new_props["width"] = max_right - new_props["left"]
                    max_bottom = max(b[k][1]["top"] + b[k][1]["height"], v[1]["top"] + v[1]["height"])
                    new_props["height"] = max_bottom - new_props["top"]

                    out[k] = (new_str, new_props)
            return out

        if len(l) < 2:
            return l

        m = [l[0]]
        for x in l[1:]:
            if len(x) >= min_cols:
                m.append(x)
            else:
                # Fewer than min_cols columns - merge up!
                m[-1] = merge_up(m[-1], x)
        return m

    def remove_empty_cols(self, a):
        ks = sorted({c: None for x in a for c, y in enumerate(x) if y != ''}.keys())
        return [[x[k] for k in ks] for x in a]

    # take a list of dicts indexed by left pos, and return a
    # sorted list of lists
    def merge_nearby_cols(self, a, delta=7):
        prev = None
        cols = sorted({y: None for x in a for y in x}.keys())
        merged_cols = []
        for x in cols:
            if prev is not None and x-prev < delta:
                merged_cols[-1].append(x)
            else:
                merged_cols.append([x])
            prev = x
        return [[''.join([x.get(c, '') for c in mc]) for mc in merged_cols] for x in a]

    def _page_to_blocks(self, page_num):
        page = self._xml.xpath('//page[@number="%d"]' % (page_num))[0]
        blocks = self._get_text(page)

        # d = defaultdict(dict)
        # for x in blocks:
        #     top = x[1]["top"]
        #     left = x[1]["left"]
        #     d[top][left] = x

        # n = self.merge_nearby_rows(d)
        # self.m = self.merge_continued_cells(self.n)
        # self.z = self.merge_nearby_cols(self.m)
        # return [[y for _, y in sorted(x.items())] for x in n]

        return blocks

    def _get_text(self, page):
        out = []
        for x in page.getchildren():
            block = self._get_text_recursive(x)
            if block[0] != '':
                if block[0] == 'plc.':
                    out[-1] = ('%s plc.' % out[-1][0], out[-1][1])
                else:
                    out.append(block)
        return out

    def _get_text_recursive(self, el):
        properties = {}
        if el.attrib != {}:
            for k, v in el.attrib.items():
                try:
                    properties[k] = int(v)
                except ValueError:
                    properties[k] = v
        text = unicode(el.text.strip()) if el.text is not None else ''
        for child in el.getchildren():
            child_text, child_properties = self._get_text_recursive(child)
            text += child_text
            properties = dict(properties.items() + child_properties.items())
        return text, properties


def from_file(filename):
    return PDFtoXML(filename)
