
# coding: utf-8

# In[1]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# In[2]:

osmfile = "san-jose.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Loop", "Circle", "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way", "Terrace", "Highway","Expressway", "East", "West", "Bellomy", "Winchester", "Oro", "1","Esquela", "Bascom", "6", "Plaza","Walk","Portofino","Napoli","Paviso","Barcelona","Volante","Sorrento","Franklin","Real", "Julian", "Flores", "Saratoga", "0.1","7.1", "Presada", "Row", "Alley", "Alameda", "Seville", "Montaña", "Palamos", "Marino", "Oaks", "Luna", "Madrid", "Mall", "Hamilton", "81", "114", "Robles", "Hill"]


# In[3]:

#this mapping was created after several iterations of the audit function
mapping = { "St": "Street",
            "St.": "Street",
           "street":"Street",
            "Rd": "Road",
           "Rd.": "Road",
            "Ave": "Avenue",
           "ave": "Avenue",
           "Hwy": "Highway",
           "court": "Court",
           "Sq": "Square",
           "Blvd": "Boulevard",
           "Boulvevard": "Boulevard",
           "Blvd.": "Boulevard",
           "Ln": "Lane",
           "Dr": "Drive",
           "Cir": "Circle",
           "Ct" : "Court",
           "Pkwy": "Parkway"
           
            }


# In[8]:

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    if re.search(u'Montaña',tag.attrib['v']): #this line is added due to a unicode error with python 2. this line bypasses it when it comes across this street name
                        continue
                    else:
                        audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            name = re.sub(street_type_re, mapping[street_type], name)

    return name


# In[9]:

st_types = audit(osmfile)
#print out updated names
for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name


# In[ ]:



