from data_models import models


class NamedEntityController:
    def __init__(self, name=False):
        self.name = name
        self.identity = name
        self.n = models.NounPhrase(self.name)
        self.n.fetch()
        self.exists = self.n.exists
        self.exclude = ['Named Entity', 'Noun Phrase']
        self._properties = {}
        self.is_mp = False
        self.has_statements = False
        self.has_associated = False
        self.has_mentions_in_media = False
        self.has_mentions_in_debate = False
        self.has_positions = False
        self._set_properties()

    def labels(self):
        for label in self.labels:
            yield label

    def mentions_in_media(self):
        public = [
            (d[0], d[1]) for d in self._properties["documents"]
            if 'Public Media' in d[1]
        ]
        for doc, labels in public:
            yield {
                "doc_id": doc["doc_id"],
                "publication": doc["publication"],
                "title": doc["title"],
                "content": doc["content"],
                "summary": doc["summary"],
                "link": doc["link"],
                "sentiment": doc["sentiment_mean"],
                "subjectivity": doc["subjectivity_mean"]
            }

    def mentions_in_debate(self):
        debate = [
            (d[0], d[1]) for d in self._properties["documents"]
            if 'Debate Argument' in d[1]
        ]
        for doc, labels in debate:
            yield {
                "doc_id": doc["doc_id"],
                "publication": doc["publication"],
                "title": doc["title"],
                "content": doc["content"],
                "link": doc["link"],
                "summary": doc["summary"],
                "sentiment": doc["sentiment_mean"],
                "subjectivity": doc["subjectivity_mean"]
            }

    def statements(self):
        for statement in self._properties["statements"]:
            yield {
                "doc_id": statement["doc_id"],
                "title": statement["title"],
                "summary": statement["summary"],
                "sentiment": statement["sentiment_mean"],
                "subjectivity": statement["subjectivity_mean"]
            }

    def positions(self):
        for position in self._properties["positions"]:
            yield position

    def terms_in_parliament(self):
        for term in self._properties["terms"]:
            if term["left_house"] == "9999-12-31":
                left = "Still in Office"
            else:
                left = term["left_house"]
            yield {
                "constituency": term["constituency"],
                "party": term["party"],
                "entered": term["entered_house"],
                "left": left
            }

    def associated_names(self):
        names = [
            (d[0], d[1]) for d in self._properties["associated"]
            if self._get_node_name(d[0])[1] == "name"
        ]
        for node, count in names[:100]:
            details = self._get_node_name(node)
            if details[1] == "name":
                yield {
                    "edge": details[0],
                    "type": details[1],
                    "count": count
                }

    def associated_topics(self):
        topics = [
            (d[0], d[1]) for d in self._properties["associated"]
            if self._get_node_name(d[0])[1] == "term"
        ]
        for node, count in topics[:100]:
            details = self._get_node_name(node)
            if details[1] == "term":
                yield {
                    "edge": details[0],
                    "type": details[1],
                    "count": count
                }

    def _set_properties(self):
        if self.n.exists:
            self._get_node_properties()
            self.name = self._properties["name"]
            self.labels = self._properties["labels"]
            self._set_documents()
            self._set_mp_properties(self.n.vertex)

    def _get_node_properties(self):
        stats = [x for x in self.n.get_stats()]
        self._properties["name"] = self.n.vertex["noun_phrase"]
        self._properties["sentence_count"] = stats[0]
        self._properties["document_count"] = stats[1]
        self._properties["term_count"] = stats[2]
        self._properties["labels"] = [
            l for l in self.n.vertex.get_labels() if l not in self.exclude
        ]
        self._properties["associated"] = [l for l in self.n.get_associated()]
        if len(self._properties["associated"]) > 0:
            self.has_associated = True

    def _set_documents(self):
        if self._properties["document_count"] > 0:
            self._has_mentioned_in = True
            documents = [(d, list(d.get_labels())) for d in self.n.get_documents()]
            doc_labels = [doc[1] for doc in documents]
            self._properties["documents"] = documents
            for labels in doc_labels:
                if 'Public Media' in labels:
                    self.has_mentions_in_media = True
                if 'Debate Argument' in labels or 'Argument' in labels:
                    self.has_mentions_in_debate = True
        else:
            self._properties["documents"] = []

    def _set_mp_properties(self, node):
        if "Member of Parliament" in self._properties["labels"]:
            self.is_mp = True
            self.has_positions = True
            self._properties["party"] = node["party"]
            self._properties["guardian_url"] = node["guardian_url"]
            self._properties["publicwhip_url"] = node["publicwhip_url"]
            self._properties["statements"] = self._get_statements()
            self._properties["positions"] = self._get_positions()
            self._properties["terms"] = self._get_terms()

    def _get_statements(self):
        statements = [s for s in self.n.get_statements()]
        if len(statements) > 0:
            self.has_statements = True
        return statements

    def _get_positions(self):
        positions = []
        for p in self.n.get_positions():
            positions.append(p["noun_phrase"])
        positions.append("Member of Parliament")
        return positions

    def _get_terms(self):
        return [t for t in self.n.get_terms_in_parliament()]

    def _get_node_name(self, node):
        #print node
        if "noun_phrase" in node:
            return node["noun_phrase"], "name"
        if "term" in node:
            return node["term"], "term"
        elif "sentence" in node:
            return node["sentence"], "sentence"
        elif "title" in node:
            return node["title"], "document"

    def show_properties(self):
        for prop in self._properties:
            if prop in ["outgoing", "incoming"]:
                print "*", prop
                for rel in self._properties[prop]:
                    self._print_out(rel, " ")
            else:
                self._print_out(prop, self._properties[prop])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)

