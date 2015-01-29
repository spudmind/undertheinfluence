import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import OperationFailure


class MongoInterface:
    def __init__(self):
        self._logger = logging.getLogger('')
        self.client = MongoClient()
        self.db = self.client.spud
        self._collections()
        self.duplicate_error = DuplicateKeyError
        self.index_error = OperationFailure

    def _collections(self):
        self._logger.debug(self.db.collection_names())


