import logging
from pymongo import MongoClient, database, collection

# from pymongo.errors import DuplicateKeyError
# from pymongo.errors import OperationFailure


class MongoInterface:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self._db = database.Database(MongoClient(), 'spud')

        self.print_collections()
        # self.duplicate_error = DuplicateKeyError
        # self.index_error = OperationFailure

    # print all collections
    def print_collections(self):
        self._logger.debug(self._db.collection_names())

    # return all documents in a collection
    def fetch_all(self, _collection):
        return self.query(_collection)

    # return specific documents in a collection
    def query(self, _collection, **kwargs):
        query = kwargs.get('query', None)
        per_page = kwargs.get('per_page', 20)
        page = kwargs.get('page', 1)
        # figure out how many records to skip
        offset = per_page * (page-1)

        q = collection.Collection(self._db, _collection)
        if query is not None:
            q = q.find(query)
        else:
            q = q.find()
        q = q.limit(per_page)
        q = q.skip(offset)

        total =q.count()
        has_more = offset + per_page < total
        meta = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': has_more,
        }
        return list(q), meta

    # save document to a collection
    def save(self, _collection, document):
        collection.Collection(self._db, _collection).save(document)
