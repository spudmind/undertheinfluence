import logging
from pymongo import MongoClient, database, collection


class MongoInterface:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = database.Database(MongoClient(), 'spud')
        #self.print_collections()

    # print all collections
    def print_collections(self):
        self._logger.debug(self.db.collection_names())

    # return all documents in a collection
    def fetch_all(self, _collection, paged=True):
        if paged:
            return self.query(_collection)
        else:
            q = collection.Collection(self.db, _collection)
            return list(q.find())

    # return specific documents in a collection
    def query(self, _collection, **kwargs):
        query = kwargs.get('query', None)
        per_page = kwargs.get('per_page', 20)
        page = kwargs.get('page', 1)
        # figure out how many records to skip
        offset = per_page * (page-1)
        q = collection.Collection(self.db, _collection)
        if query is not None:
            q = q.find(query)
        else:
            q = q.find()
        q = q.limit(per_page)
        q = q.skip(offset)

        total = q.count()
        has_more = offset + per_page < total
        meta = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': has_more,
        }
        return list(q), meta

    def sum(self, _collection, **kwargs):
        field = kwargs.get('field', None)
        q = collection.Collection(self.db, _collection)
        pipe = [
            {'$group': {'_id': None, 'total': {'$sum': field}}}
        ]
        result = q.aggregate(pipe)
        return result["result"][0]["total"]

    def count(self, _collection):
        q = collection.Collection(self.db, _collection)
        return q.count()

    # save a document to a collection
    def save(self, _collection, document, **kwargs):
        return collection.Collection(self.db, _collection).save(document, **kwargs)

    # update a document in a collection
    def update(self, _collection, document, update):
        return collection.Collection(self.db, _collection).update(document, update)

    def drop(self, _collection):
        q = collection.Collection(self.db, _collection)
        return q.drop()
