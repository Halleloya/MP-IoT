from pymongo import MongoClient

class MongoService(object):
    def __init__(self):
        atlas_uri = "mongodb+srv://<NAME:NAME@cluster0.XXXXXX.mongodb.net>/?retryWrites=true&w=majority"
        db_name = "<YOUR-DB-NAME>"
        self.client = MongoClient(atlas_uri)
        self.database = self.client[db_name]

    def create_policy(self, policy):
        new_policy = self.database["policies"].insert_one(policy)

    def create_thing(self, thing):
        new_thing = self.database["things"].insert_one(thing)
    
    def delete_thing(self, thing_id):
        query = {"id": thing_id}
        things = self.database["things"]
        things.delete_one(query)

    def find_policies(self, criteria):
        policies = self.database["policies"].find(criteria)
        return policies
    
    def find_things(self, criteria):
        things = self.database["things"].find(criteria)
        return things

    def drop_collection(self, name):
        collection = self.database[name]
        collection.drop()
    
