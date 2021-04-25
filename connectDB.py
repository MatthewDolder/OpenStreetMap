from pymongo import MongoClient

def cMongodb_conn(database_name):
    #This function a returns a connect to the local Mongo server.
    # source: https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb

    # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
    client = MongoClient("localhost:27017")

    ### uncomment to see health of mongo:
    # db = client.admin
    # serverStatusResult = db.command("serverStatus")
    # pprint(serverStatusResult)
    ######################################

    # connect to street_map_collection for San Antonio
    db = client[database_name]

    #check if collections exists, if not, create
    #cols = db.list_collection_names()
    #print(cols)


    return db


def initializeDB(db):
    #Clears out the database from the previous run
    db.nodes.delete_many({})
    db.ways.delete_many({})
    db.relations.delete_many({})
    db.other.delete_many({})
