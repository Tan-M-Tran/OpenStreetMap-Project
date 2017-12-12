
# coding: utf-8

# In[2]:

import xml.etree.cElementTree as ET
import pprint
import re
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# In[ ]:




# In[3]:

osmfile = "san-jose.osm"
from collections import defaultdict
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#These are the exceptions found during the auditing process
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Loop", "Circle", "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way", "Terrace", "Highway","Expressway", "East", "West", "Bellomy", "Winchester", "Oro", "1","Esquela", "Bascom", "6", "Plaza","Walk","Portofino","Napoli","Paviso","Barcelona","Volante","Sorrento","Franklin","Real", "Julian", "Flores", "Saratoga", "0.1","7.1", "Presada", "Row", "Alley", "Alameda", "Seville", "Monta\xf1a", "Palamos", "Marino", "Oaks", "Luna", "Madrid", "Mall", "Hamilton", "81", "114", "Robles", "Hill"]


# In[4]:

#This mapping was creating from the initial audit
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


# In[5]:

#function to take in the street name and update it using the mapping
def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            name = re.sub(street_type_re, mapping[street_type], name)

    return name


# In[6]:

#function to extract the main 5 digit postal code
def update_postcode(postcode):
    # new regular expression pattern
    if postcode == 'CUPERTINO':
        clean_postcode = 95014
    else:
        search = re.match(r'^\D*(\d{5}).*', postcode)
    # select the group that is captured
        clean_postcode = search.group(1)
    return clean_postcode


# In[7]:

import csv
import codecs
import cerberus
import schema
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"


# In[8]:

SCHEMA = schema.schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# In[20]:

#main function used to shape and clean the elements
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=problemchars, default_tag_type='regular'):
    

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  
    count = 0

    
    if element.tag == 'node':
        for key in NODE_FIELDS:
            node_attribs[key] = element.attrib[key]
        for child in element:
            if child.tag == 'tag':
                node_tag = {}
                
                
                if problemchars.match(child.attrib['k']):
                    continue
                elif lower_colon.match(child.attrib['k']):
                    node_tag['id'] = element.attrib['id']
                    node_tag["type"] = child.attrib["k"].split(":", 1)[0]
                    node_tag["key"] = child.attrib["k"].split(":", 1)[1]
                    
                    if child.attrib['k'] == "addr:street":
                        
                        if re.search(u'Montaña',child.attrib['v']): #this line was added to bypass a unicode error that occured due to the ñ character 
                            node_tag['value'] = child.attrib['v']
                        else:
                            node_tag['value'] = update_name(child.attrib['v'],mapping)
                    elif child.attrib['k'] == "addr:postcode":
                        node_tag['value'] = update_postcode(child.attrib['v']) #pass the postal code to the cleaning function
                    else:
                        node_tag['value'] = child.attrib['v']
                
        
                else:
                    node_tag['id'] = element.attrib['id']
                    node_tag['key'] = child.attrib['k']
                    node_tag['type'] = 'regular'
                    node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for key in WAY_FIELDS:
            way_attribs[key] = element.attrib[key]
        for child in element:
            if child.tag == 'tag':
                way_tag = {}
                way_tag['id'] = element.attrib['id']
                if child.attrib['k'] == "addr:postcode":
                    way_tag['value'] = update_postcode(child.attrib['v'])
                else:
                    way_tag['value'] = child.attrib['v']
                if ':' in child.attrib['k']:
                    loc = child.attrib['k'].find(':')
                    key = child.attrib['k']
                    way_tag['type'] = key[:loc]
                    way_tag['key'] = key[loc+1:]
                else:
                    way_tag['key'] = child.attrib['k']
                    way_tag['type'] = 'regular'
                tags.append(way_tag)
        for tag in element.iter("nd"):
            way_node = {}
            way_node['id'] = element.attrib['id']
            way_node['node_id'] = tag.attrib['ref']
            way_node['position'] = count
            count += 1
            
            way_nodes.append(way_node)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# In[10]:

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# In[11]:

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[ ]:




# In[12]:

#the previous few functions were taken from the exercise to prep the csv files to be inserted into the database
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# In[21]:

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(osmfile, validate=False)


# In[ ]:



