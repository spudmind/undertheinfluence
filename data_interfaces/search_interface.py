from elasticsearch import Elasticsearch


class SearchInterface:
    def __init__(self):
        self._es = Elasticsearch()
        self._db = "spud"

    def search(self, collection, search_query):
        return self._es.search(
            index=self._db, doc_type=collection, body=search_query
        )
