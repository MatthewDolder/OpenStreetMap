# Open Street Map Data Wrangling Project
    
I chose the city of San Antonio, TX: https://www.openstreetmap.org/relation/253556

The San Antonio osm download came from the overpass API: https://overpass-api.de/api/map?bbox=-99.0555,29.1863,-97.9802,29.7304

OSM Filesize Uncompressed: 512MB

I parsed the XML using cElementTree iterparse and pushed the records into a local MongoDB installation using PyMongo.
Using Beautiful Soup 4, I scraped an HTML file from USPS containing street suffix abbreviations: https://pe.usps.com/text/pub28/28apc_002.htm

A smaller OSM file is attached with the code submission.  It represents a few blocks of the city.

The queries below are run against the larger dump of the entire city. 



```python
#connect to the database
from pymongo import MongoClient
client = MongoClient("localhost:27017")
db = client["street_map_410"]

```

## Query the Database for Statistics
### 1. size of the file
    



```python
dataSize = str(round(db.command("dbstats")["dataSize"] / 1024 / 1024))
display(dataSize + " MB")
```


    '564 MB'


### 2. number of unique users


```python
num_users = len(db.nodes.find({"user": {"$exists": 1}}, {"user": 1, "_id": 0}).distinct("user"))
display("number of users: " + f'{num_users:,}')
```


    'number of users: 1,610'


### 3. number of nodes and ways


```python
num_nodes = (db.nodes.count_documents({}))
num_ways = (db.ways.count_documents({}))
display("nodes collection contains " + f'{num_nodes:,}' + " documents.")
display("ways collection contains " + f'{num_ways:,}' + " documents.")

```


    'nodes collection contains 2,386,694 documents.'



    'ways collection contains 298,076 documents.'


### 4. number of residential streets in ways



```python
streets = len(db.ways.find({"tag.highway": "residential", "tag.name": {"$exists": 1}}, {"tag.name": 1, "_id": 0}).distinct("tag.name"))
display("number of residential streets: " + f'{streets:,}')

```


    'number of residential streets: 29,045'


### 5. number and types of highway nodes


```python
#reference: https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

from bson.son import SON
pipeline = [
            {"$unwind": "$tag"},
            {"$match": {"tag.k":"highway"}},
            {"$group": {"_id": "$tag", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
            ]
tags = db.nodes.aggregate(pipeline)
display(list(tags))
```


    [{'_id': {'k': 'highway', 'v': 'turning_circle'}, 'count': 13782},
     {'_id': {'k': 'highway', 'v': 'traffic_signals'}, 'count': 2797},
     {'_id': {'k': 'highway', 'v': 'street_lamp'}, 'count': 2176},
     {'_id': {'k': 'highway', 'v': 'crossing'}, 'count': 2075},
     {'_id': {'k': 'highway', 'v': 'turning_loop'}, 'count': 851},
     {'_id': {'k': 'highway', 'v': 'stop'}, 'count': 815},
     {'_id': {'k': 'highway', 'v': 'give_way'}, 'count': 114},
     {'_id': {'k': 'highway', 'v': 'motorway_junction'}, 'count': 20},
     {'_id': {'k': 'highway', 'v': 'bus_stop'}, 'count': 14},
     {'_id': {'k': 'highway', 'v': 'mini_roundabout'}, 'count': 8},
     {'_id': {'k': 'highway', 'v': 'construction'}, 'count': 2},
     {'_id': {'k': 'highway', 'v': 'services'}, 'count': 1},
     {'_id': {'k': 'highway', 'v': 'checkpoint'}, 'count': 1}]


### 6. number of document submissions per year



```python
#source: https://pymongo.readthedocs.io/en/stable/examples/aggregation.html
#https://docs.mongodb.com/manual/aggregation/
from bson.son import SON

pipeline = [{"$project": {"_id" : 0,"year":{"$substrBytes":["$timestamp",0,4]}}},
            {"$group" : {"_id" : "$year","numdocs":{"$sum": 1}}},
            {"$sort" : {"_id":-1}}
           ]

years = db.nodes.aggregate(pipeline)
for y in years:
    display(y["_id"] + ":" + str(y["numdocs"]))

```


    '2021:160489'



    '2020:472031'



    '2019:414132'



    '2018:151831'



    '2017:138396'



    '2016:95203'



    '2015:182256'



    '2014:97784'



    '2013:68244'



    '2012:159966'



    '2011:91342'



    '2010:34821'



    '2009:318009'



    '2008:2190'


## About the enclosed python project

To execute the project run `main.py`. This connects to a local MongoDB instance and sets up the database.  

`openXML.parseXML(db,filepath)` is called next which uses cElementTree to parse the OSM file, create JSON records and push them into Mongo into one of three collections (nodes, ways, relations). 

A sample json document for a way: 

```Json 
{'id': '15110885', 'version': '11', 'timestamp': '2021-02-17T11:51:08Z', 'changeset': '99449870', 'uid': '10271447', 'user': 'grandhs', 'nd': ['149258796', '149258798'], 'tag': {'highway': 'residential', 'name': 'Lakeside Drive', 'tiger:cfcc': 'A41', 'tiger:county': 'Bandera, TX', 'tiger:name_base_1': 'Lakeside', 'tiger:name_type': 'Dr', 'tiger:reviewed': 'no'}}
```

Database populated, I create a pyMongo query to find all residential highways:
```Json
{"tag.highway": "residential", "tag.name": {"$exists": 1}}
```

Function `clean_streets.getCleanStreets(db,query)` is called which runs the Mongo query and creates a distinct list of street names.  Function `abbreviation_map.getReplacements` scrapes the list of postal suffixes and builds regex. 

For each unique street name, I run the list of regex commands.  If a match is found, it is returned back to main as a dictionary of search and replace shown below: 

The code block below runs through the query and clean process and outputs the list of cleaned residental streets for San Antonio, TX:


```python
import clean_streets
query = {"tag.highway": "residential", "tag.name": {"$exists": 1}}
cleanstreets = clean_streets.getCleanStreets(db,query)
```

    Balcon Is  :  Balcon Island
    Blanco Ky  :  Blanco Key
    Creek Cor  :  Creek Corner
    Falcons Ht  :  Falcons Heights
    Fawn Mnt  :  Fawn Mount
    Nike CIrcle  :  Nike Circle
    Oilfield Rds  :  Oilfield Roads
    Painted Tracks  :  Painted Track
    Reading Green Blvd  :  Reading Green Boulevard
    Sandoval street  :  Sandoval Street
    Scaup court  :  Scaup Court
    Sulphur Trails  :  Sulphur Trail
    Sunnyview Trails  :  Sunnyview Trail
    WInding RIver  :  WInding River
    Wetmore Knl  :  Wetmore Knoll
    Wild Trls  :  Wild Trail
    Wind river  :  Wind River
    glag lane  :  glag Lane
    loving path  :  loving Path
    

The final step is to call `clean_streets.CleanTheStreets(cleanstreets,db)` which accepts the dictionary of old and new street names.  It steps through each one and runs a search and replace in Mongo: 

```Python
for old,new in cleanstreets.items():
        db.ways.update_many({"tag.highway": "residential", "tag.name": old}, {"$set": {"tag.name": new}})
```

## Problems encountered

### 1. memory errors
The first pass I used cElementtree without iterparse.  This worked great for small datasets, however when I tried to process all of San Antonio, I ran into errors.  I then switched to iterparse and used the clear() method after each node. 

### 2. weird HTML table
The HTML table scraped from the USPS site is in a strange format.  The result was a list of dictionaries where the first record has 3 columns, the next several records had only 1 column, etc.  To fix, I had to iterate through the list and create a fresh dictionary repeating the values in the first column.  A sample of the final set: 
```json
{'ALLEE': 'Alley', 'ALLEY': 'Alley', 'ALLY': 'Alley', 'ALY': 'Alley', 'ANEX': 'Anex', 'ANNEX': 'Anex', 'ANNX': 'Anex', 'ANX': 'Anex', 'AV': 'Avenue', 'AVE': 'Avenue'}
```

### 3. Bad suffix
The "Arc" suffix was turning streets which were supposed to end in "Arc" into "Arcade".  I removed this suffix.  

### 4. performance problems itterating the list of street names X the list of known suffixes
After some debugging, I found I was performing the HTML scrape for every street name.  Removing that made the performance good enough for the San Antonio dataset.  

## Ideas for Improvement

### 1. Expanding the type of streets

I limited the clean up to highway = residental.  The cleanup could be expanded for all highway types.  However, the USPS codes don't work well with business names.  For instance the "Panda Express" service road is changed into "Panda Expressway".  Some exceptions would need to be included. 


```python
streets = db.ways.find({"tag.highway": "service", "tag.name": "Panda Express"}, {"tag.highway" : 1,"tag.name": 1, "_id": 0})
for s in streets:
    display(s)
```


    {'tag': {'highway': 'service', 'name': 'Panda Express'}}


By querying the database and adding to the filter, I was able to include other highway types including service roads while eliminating business names and private roads.  This found 1,692 candidates for cleanup and of those found 4 roads to clean.  Shown below. 


```python
query={"tag.highway":{"$in":['living_street','motorway','motorway_link','path','primary','primary_link','proposed','secondary','secondary_link','service','tertiary','tertiary_link','trunk','trunk_link']}, 
       "tag.access":{"$ne":"private"}, 
       "tag.name":{"$exists":1, "$ne":"Private Road"},
       "tag.service":{"$ne":"drive-through"}}
streets = db.ways.find(query).distinct("tag.name")
display("Street Name Candiates for Cleanup: " + str(len(streets)))

```


    'Street Name Candiates for Cleanup: 1692'



```python
cleanstreets = clean_streets.getCleanStreets(db,query)
```

    Jagge lane  :  Jagge Lane
    Unnamed Pr  :  Unnamed Prairie
    Valley Trails  :  Valley Trail
    plantation drive  :  plantation Drive
    

The disadvantage of the approach above is that a larger dataset, such as all of Texas,  will likely produce more edge cases.  That will require more adjustments to the filter.  

### 2. Cleaning up municipal services
San Antonio Fire Stations are not in a consistant format.  We could do a regex search and replace


```python
import re
#Reference: 
#https://stackoverflow.com/questions/55617412/how-to-perform-wildcard-searches-mongodb-in-python-with-pymongo
fire = db.ways.find({"tag.name": {"$regex": "San Antonio Fire.+\d$"}}).distinct("tag.name")

p = re.compile('.+?(\d+)')

firere = {}
for f in fire:
    if p.match(f):
        firere[f] = "San Antonio Fire Station #" + p.match(f).group(1)
display(firere)
```


    {'San Antonio Fire Department Station #22': 'San Antonio Fire Station #22',
     'San Antonio Fire Department Station Number 38': 'San Antonio Fire Station #38',
     'San Antonio Fire Station #19': 'San Antonio Fire Station #19',
     'San Antonio Fire Station #29': 'San Antonio Fire Station #29',
     'San Antonio Fire Station #41': 'San Antonio Fire Station #41',
     'San Antonio Fire Station 1': 'San Antonio Fire Station #1',
     'San Antonio Fire Station 11': 'San Antonio Fire Station #11',
     'San Antonio Fire Station 27': 'San Antonio Fire Station #27',
     'San Antonio Fire Station 31': 'San Antonio Fire Station #31',
     'San Antonio Fire Station 32': 'San Antonio Fire Station #32',
     'San Antonio Fire Station 34': 'San Antonio Fire Station #34',
     'San Antonio Fire Station 35': 'San Antonio Fire Station #35',
     'San Antonio Fire Station 4': 'San Antonio Fire Station #4',
     'San Antonio Fire Station 40': 'San Antonio Fire Station #40',
     'San Antonio Fire Station 43': 'San Antonio Fire Station #43',
     'San Antonio Fire Station 46': 'San Antonio Fire Station #46',
     'San Antonio Fire Station 47': 'San Antonio Fire Station #47',
     'San Antonio Fire Station 54': 'San Antonio Fire Station #54',
     'San Antonio Fire Station No. 45': 'San Antonio Fire Station #45'}


The disadvantage of the approach above is that it won't work for other cities.  An improvement would be to pull the city name from the database dynamically.  Also, many towns will only have 1 fire station which may not have a number at the end.  

### 3.  Finding new roads

San Antonio is going through a period of rapid expansion.  It is easy to drive to a new neighborhood and confuse Google Maps.  However, realtors and builders are quick to list street names to new lots on real estate websites.  Here is one such development on Zillow: https://www.zillow.com/community/valley-ranch/29261528_plid/ The streets listed here do not show up on open street map search. 

It would be interesting project to scrape the popular real estate websites and list nodes and ways which need to be added to open street map.  Possibly the builders would be willing to provide a feed which could be cleaned and added automatically.  




```python

```
