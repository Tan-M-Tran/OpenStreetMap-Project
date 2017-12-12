
# coding: utf-8

# In[1]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# In[2]:

OSMFILE = 'san-jose.osm'


# In[3]:

#this function determines if the element being passed through is the postal code
def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


# In[4]:

def update_postcode(postcode):
    # new regular expression pattern
    if postcode == 'CUPERTINO':
        clean_postcode = 95014
    else:
        search = re.match(r'^\D*(\d{5}).*', postcode)
    # select the group that is captured
        clean_postcode = search.group(1)
    return clean_postcode


# In[5]:

#this function builds a dictionary of good zip codes and zip codes we want to fix. The zip codes we want to fix contain more than 5 digits
def audit_zipcode(invalid_zipcodes, good_zipcodes, zipcode):
    if re.match(r'^\d{5}$', zipcode):
        good_zipcodes[zipcode] += 1
    else:
        invalid_zipcodes[zipcode] += 1


# In[6]:

#this function iterates through the elements and passes any postal codes onto the audit_zipcode function and keeps a dictionary of all postal codes we want to fix
def auditzip(OSMFILE):
    datafile = open(OSMFILE, "r")
    invalid_zipcodes = defaultdict(int)
    good_zipcodes = defaultdict(int)
    counter = 0
    for event, elem in ET.iterparse(datafile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    audit_zipcode(invalid_zipcodes, good_zipcodes, tag.attrib['v'])
                    
                    counter += 1
    datafile.close()
    return invalid_zipcodes


# In[7]:

zip_types = auditzip(OSMFILE) #we run the audit and print out the dictionary of bad postal codes to see what systematic problems occur
print zip_types

