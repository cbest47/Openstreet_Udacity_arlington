from pymongo import MongoClient
import xml.etree.cElementTree as ET
from collections import defaultdict
from collections import deque
import re
import pprint

#Opening my street data for the city of Arlington, VA downloaded from OpenStreetMap
arlington_xml_data = open("arlington_xml_data", "r")

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)
experiment = {}

#List of unwanted street types
bad_list = ['Southwest', 'S.W.','Southeast', 'Southwest', 'St.', 'Hwy', 'North1', 'Northeast', 'Northwest', 'Ave.', 'Southeast\\']
#List of expected street types
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Trail", "Parkway", "Commons"]
#Below is my connection to my mongodb database for insterting cleaned data
client = MongoClient(port=27017)
db = client.project2try2

def audit_street_types(street_types, street_name):
    x = street_type_re.search(street_name)
    if x:
        street_type = x.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit():
    for event, elem in ET.iterparse(arlington_xml_data, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_types(street_types, tag.attrib['v'])
    #pprint.pprint(dict(street_types))
    return(dict(street_types))

#Making sure unwanted street types don't make their way into the database
def create_default_dict_structure(street_types):
    for street in street_types:
        if street not in bad_list:
            experiment.setdefault(street, [])

#trying to make a dict {} and just append each list[] after making certain it's clean then I will create a function to iterate over the dict to push those to MongoDB.
def change_data(street_types_dict):
    for x in street_types_dict:

        if x == 'Southwest':
            for y, street in enumerate(street_types_dict[x]):
                #check to see if not in the list of streets we don't want in our new dictionary
                #if street not in bad_list:
                    name = street.split(' ')
                    #iterate over the street name after splitting it to check for term you want to replace

                    for i, n in enumerate(name):
                        if n == 'Southwest':
                            name[i] = 'SW'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Ave.':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Ave.':
                            name[i] = 'Ave'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'S.W.':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'S.W.':
                            name[i] = 'SW'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Southeast\\':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Southeast\\':
                            name[i] = 'SE'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'St.':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'St.':
                            name[i] = 'St'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Southeast':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Southeast':
                            name[i] = 'SE'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'North1':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'North1':
                            name[i] = 'North'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Northeast':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Northeast':
                            name[i] = 'NE'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Northwest':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Northwest':
                            name[i] = 'NW'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        if x == 'Hwy':
            for y, street in enumerate(street_types_dict[x]):
                    name = street.split(' ')
                    for i, n in enumerate(name):
                        if n == 'Hwy':
                            name[i] = 'Highway'
                            experiment.setdefault(name[i], [])
                            new = ' '.join(name)
                            experiment[name[i]].append(new)
        else:
            if x not in bad_list:
                experiment.setdefault(x, [])
                for street in street_types_dict[x]:
                    experiment[x].append(street)

# Calling all of the functions I've created before I insert the data from the "experiment" dictionary into MongoDB

audit()
create_default_dict_structure(street_types)
change_data(street_types)
#pprint.pprint(experiment)

#The function used to shape the database entries and then insert them
def db_insert(experiment):
    street_type = 'street_type'
    street_name = 'street_name'
    for x in experiment:
        street_insert = {
            street_type : x,
            street_name : experiment[x]
        }
        result = db.streets.insert_one(street_insert)
        print(result.inserted_id)



db_insert(experiment)
