from data_models import core
from data_models import models


class DocumentController:
    def __init__(self, doc_id=False):
        self.doc_id = doc_id
        self.d = core.Document(self.doc_id)
        self.d.fetch()
        self.exists = self.d.exists
        self.title = None
        self.content = None
        self.publication = None
        self.has_associated = False
        self.is_document = True
        self._properties = {}
        self._set_properties()

    def associated_names(self):
        for mention in self._properties["name_mentions"]:
            if mention["type"] == "name":
                yield mention

    def associated_topics(self):
        for mention in self._properties["term_mentions"]:
            if mention["type"] == "term":
                yield mention

    def _set_properties(self):
        if self.d.exists:
            self._get_node_properties()
            self.title = self._properties["title"]
            self.content = self._properties["content"]
            self.publication = self._properties["publication"]

    def _get_node_properties(self):
        self._properties["title"] = self.d.vertex["title"]
        self._properties["content"] = self._format(self.d.vertex["content"])
        self._properties["publication"] = self.d.vertex["publication"]
        self._set_mentions()

    def _set_mentions(self):
        get_names = self.d.get_doc_features("Named Entity")
        get_terms = self.d.get_doc_features("Unique Term")
        self._properties["name_mentions"] = [
            {
                "type": "name",
                "edge": n[0]["noun_phrase"],
                "count": n[1]
            } for n in get_names
        ]
        self._properties["term_mentions"] = [
            {
                "type": "term",
                "edge": t[0]["term"],
                "count": t[1]
            } for t in get_terms
        ]
        self._properties["top_mentions"] = \
            self._properties["name_mentions"][:3] + \
            self._properties["term_mentions"][:3]
        if len(self._properties["top_mentions"]) > 0:
            self.has_associated = True

    def show_properties(self):
        for prop in self._properties:
            if prop in ["outgoing", "incoming"]:
                print "*", prop
                for rel in self._properties[prop]:
                    self._print_out(rel, " ")
            else:
                self._print_out(prop, self._properties[prop])

    def _format(self, string):
        old_content = string.split("\n\n")
        new_content = ""
        for para in old_content:
            new_content += "<p>%s</p>" % para
        return new_content

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)

