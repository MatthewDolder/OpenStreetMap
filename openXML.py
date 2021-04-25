import xml.etree.cElementTree as ET


def parseroot(child,db):
    #this module accepts a single element from iterparse, steps through it creating JSON and pushes a single record into Mongo.
    #for child in root:
        print(child.tag, child.attrib)
        if child.tag == "node":
            node = child.attrib
            for thistag in child:
                if thistag.tag == "tag":
                    node['tag'] = thistag.attrib
                else:
                    print(thistag.attrib)

            db.nodes.insert_one(node)
            print(node)
        elif child.tag == "way":
            way = child.attrib
            nd = []
            ##tag = []
            splittag = {}
            for thistag in child:
                if thistag.tag == "nd":
                    nd.append(thistag.attrib['ref'])
                elif thistag.tag == "tag":
                    splittag[thistag.attrib['k']] = thistag.attrib['v']
                    # print(splittag)
                    ###tag.append(splittag)
                else:
                    print(thistag.attrib)
            way['nd'] = nd
            ##way['tag'] = tag
            way['tag'] = splittag

            db.ways.insert_one(way)
            print(way)
        elif child.tag == "relation":
            relation = child.attrib
            member = []
            tag = []
            for thistag in child:
                if thistag.tag == "member":
                    member.append(thistag.attrib)
                elif thistag.tag == "tag":
                    splittag = {}
                    splittag[thistag.attrib['k']] = thistag.attrib['v']
                    # print(splittag)
                    tag.append(splittag)
                else:
                    print(thistag.attrib)

            relation['member'] = member
            relation['tag'] = tag

            db.relations.insert_one(relation)
            print(relation)
        else:
            db.other.insert_one(child.attrib)

        return


def parseXML(db, filepath):
    #This module accepts an osm filename and parses it using ElementTree.iterpase.
    #for each element, it calls the procedure above to convert to json and push into Mongo
    ##setup dictionaries to populate
    node = {}
    way = {}
    relation = {}


    #source:  Lesson 13, section 5 of Udacity Data Wrangling nanodegree
    # https://classroom.udacity.com/nanodegrees/nd002-wgu/parts/fa83382c-7342-40a3-aa96-d66f213215d4/modules/f0471f11-208b-484a-90f1-6889d2cbc727/lessons/3deb3102-0ba1-4684-b4b1-3af4b2e8c533/concepts/8755386140923
    for event,elem in ET.iterparse(filepath,events=("start",)):
        if elem.tag in ("way","node","relation"):
            print(elem.tag)
            parseroot(elem,db)
        elem.clear() # https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse


    return

