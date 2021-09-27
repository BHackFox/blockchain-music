from pymongo import MongoClient


class Database:
    def __init__(self):
        self.cluster = MongoClient('mongodb://localhost:27017')
        self.db = self.cluster["prova"]
        self.collection = self.db["prova"]

    def insert(self,obj):
        #print(obj)
        self.collection.insert_one(obj)

    def find(self):
        obj = self.collection.find_one()
        result = JSONEncoder().encode(obj)
        return result

import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
