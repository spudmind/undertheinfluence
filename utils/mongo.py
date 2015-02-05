import logging
from pymongo import MongoClient, database, collection

# from pymongo.errors import DuplicateKeyError
# from pymongo.errors import OperationFailure


class MongoInterface:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = database.Database(MongoClient(), 'spud')

        self.print_collections()
        # self.duplicate_error = DuplicateKeyError
        # self.index_error = OperationFailure

    # print all collections
    def print_collections(self):
        self._logger.debug(self.db.collection_names())

    # return all documents in a collection
    def fetch_all(self, _collection):
        return list(collection.Collection(self.db, _collection).find())

    # save document to a collection
    def save(self, _collection, document):
        collection.Collection(self.db, _collection).save(document)
