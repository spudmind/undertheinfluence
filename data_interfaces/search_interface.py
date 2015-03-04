from elasticsearch import Elasticsearch


class SearchInterface:
    def __init__(self):
        self._es = Elasticsearch()
        self._db = "spud"

    def search(self, field, search):
        api_collections = ["api_politicians", "api_influencers", "api_government"]
        search_query = {
            "query": {
                "match": {
                    "{}".format(field): {
                        "query": u"{}".format(search),
                        "fuzziness": 2,
                        "prefix_length": 1
                    }
                }
            }
        }
        q = self._es.search(
            index=self._db, body=search_query, doc_type=api_collections
        )
        results = [r["_source"] for r in q["hits"]["hits"]]
        meta = {
            'total': len(results),
            'page': 1,
            'per_page': len(results),
            'has_more': False,
        }
        return results, meta

