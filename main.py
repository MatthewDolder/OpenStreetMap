import connectDB
import clean_streets
import openXML

def main():
    ##small test file
    filepath = 'small_sample.osm'
    #################
    ##big data file:
    #filepath = 'c:\data\410loop_san_antonio.040321.osm'

    ##way bigger data file:
    #filepath = 'c:\data\san_antonio.osm'


    #call this with the desired database name
    #it will create collections if they don't already exist.
    print("connecting to the database")
    db = connectDB.cMongodb_conn("small_sample")
    connectDB.initializeDB(db)
    print("connected")

    #the following clears the Mongo database, parses the osm file and loads into 3 collections.
    #it takes many hours to run on the san_antonio dump.
    print("now parsing: " + filepath)
    openXML.parseXML(db,filepath)

    #the following grabs a list of distinct residential street names from Mongo and creates a search/replace list.
    print("Searching for Dirty Street Names... This part takes a few minutes...")
    query = {"tag.highway": "residential", "tag.name": {"$exists": 1}}
    cleanstreets = clean_streets.getCleanStreets(db,query)

    #the following runs a search and replace on Mongo.
    print("replacing streets")
    clean_streets.CleanTheStreets(cleanstreets,db)

    print("finished")

if __name__ == "__main__":
    main()
