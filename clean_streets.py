from abbreviation_map import replaceOne
from abbreviation_map import getReplacements

def getCleanStreets(db,query):

    #find all the streets in the dataset using Mongo
    #streets = db.ways.find({"tag.highway": {"$exists": 1}, "tag.name": {"$exists": 1}}, {"tag.name": 1, "_id": 0})
    ## After some testing and junk roads such as the Panda Express drive through, I limited the search to residential highways
    #streets = db.ways.find({"tag.highway": "residential", "tag.name": {"$exists": 1}}, {"tag.name": 1, "_id": 0})
    streets = db.ways.find(query,{"tag.name": 1, "_id": 0}).distinct("tag.name")

    search_replace = {}  #create a list of search and replace for the mongo database
    # print(distinct_streets)
    replacements = getReplacements()
    for s in streets:
        # print(s)
        newStreet = replaceOne(s,replacements)
        if newStreet != s:
            search_replace[s] = newStreet

    #print("replacements Found")
    #print(search_replace)
    return(search_replace)

def CleanTheStreets(cleanstreets,db):
    #This procedure takes the list of streets we want to change and performs a search and replace in MongoDB.

    #source:
    #https://docs.mongodb.com/manual/reference/operator/aggregation/replaceOne/
    #https://docs.mongodb.com/manual/reference/method/db.collection.updateMany/
    #https://stackoverflow.com/questions/12589792/how-to-replace-substring-in-mongodb-document
    #https://docs.mongodb.com/manual/reference/method/db.collection.updateMany/#std-label-updateMany-behavior-update-expressions
    for old,new in cleanstreets.items():
        db.ways.update_many({"tag.highway": "residential", "tag.name": old}, {"$set": {"tag.name": new}})
