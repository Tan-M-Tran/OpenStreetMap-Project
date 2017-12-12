
# coding: utf-8

# In[1]:

import sqlite3
import csv
from pprint import pprint


# In[2]:

sqlite_file = 'sanjose.db'    # name of the sqlite database file

# Connect to the database
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()


# In[ ]:

#drops old tables if they previously existed in the database
cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
cur.execute('''DROP TABLE IF EXISTS nodes''')
cur.execute('''DROP TABLE IF EXISTS ways''')
cur.execute('''DROP TABLE IF EXISTS ways_tags''')
cur.execute('''DROP TABLE IF EXISTS ways_nodes''')


# In[ ]:

#create tables in the new db file
cur.execute('''
    CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)
''')
cur.execute('''
    CREATE TABLE nodes( id INTEGER,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT)
''')
cur.execute('''
    CREATE TABLE ways( id INTEGER,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT)
''')
cur.execute('''CREATE TABLE ways_tags(id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,type TEXT, FOREIGN KEY (id) REFERENCES ways(id))''')
cur.execute('''
    CREATE TABLE ways_nodes( id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id))
''')


# In[ ]:

#start inserting the data from the csv files into the tables of the database
with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'],i['value'].decode('utf-8'), i['type']) for i in dr]
    
cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)


# In[ ]:

with open('nodes.csv','rb') as fin1:
    dr = csv.DictReader(fin1) # comma is default delimiter
    to_db1 = [(i['id'], i['lat'],i['lon'], i['user'].decode('utf-8'), i['uid'], i['version'], i['changeset'], i['timestamp'].decode('utf-8')) for i in dr]

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db1)


# In[ ]:

with open('ways.csv','rb') as fin2:
    dr = csv.DictReader(fin2) # comma is default delimiter
    to_db2 = [(i['id'], i['user'].decode('utf-8'), i['uid'], i['version'], i['changeset'], i['timestamp'].decode('utf-8')) for i in dr]

cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db2)


# In[ ]:

with open('ways_tags.csv','rb') as fin3:
    dr = csv.DictReader(fin3) # comma is default delimiter
    to_db3 = [(i['id'], i['key'],i['value'].decode("utf-8"), i['type']) for i in dr]

cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db3)


# In[ ]:

with open('ways_nodes.csv','rb') as fin4:
    dr = csv.DictReader(fin4) # comma is default delimiter
    to_db4 = [(i['id'], i['node_id'],i['position']) for i in dr]
    
cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db4)


# In[ ]:

conn.commit() #commit changes
conn.close()

