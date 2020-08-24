from py2neo import Graph
from json import loads, load, dump
import requests
import random
import re
import subprocess

def emptyNone(val):
    for k in val.keys():
        if type(val[k]) is dict:
            emptyNone(val[k])
        else:
            if val[k] is None:
                val[k] = ''
    return val


with open('.gitignore') as gi:
    good = False
    # This simply checks to see if you have a connection string in your repo.
    # I use `strip` to remove whitespace/newlines.
    for line in gi:
        if line.strip() == "connect_remote.json":
            good = True
            break

pausetime = 2

if good is False:
    print("The connect_remote.json file is not in your .gitignore file. \
           Please add it!")

with open('./connect_remote.json') as f:
    data = load(f)

with open('./gh.token') as f:
    gh_token = f.read().splitlines()

graph = Graph(**data[1])

tx = graph.begin()

# The use of the >>>!!!<<< is used to show deprecation apparently.
# This returns 2255 research databases from re3data.
#  Here we're matching repos that have not been matched yet.
cypher = """MATCH (:TYPE {type:"schema:CodeRepository"})-[:isType]-(cr:OBJECT)-[:Target]-(:ANNOTATION)-[tar:Target]-(ot:OBJECT)-[:isType]-(:TYPE {type:"schema:DataCatalog"})
    WITH COLLECT(DISTINCT ot.name) AS goodies
    MATCH (ob:OBJECT)-[:isType]-(:TYPE {type:"schema:DataCatalog"})
    WHERE (NOT ob.name IN goodies)
    RETURN DISTINCT ob"""

print("Matching existing repositories")
dbs = graph.run(cypher).data()

random.shuffle(dbs)
url = []


def gen_split(x):
    split = re.search("(.*?)\s*-\s(.*)", x)
    if split == None:
        return None
    else:
        return {'package': split.group(1), 'description': split.group(2) }


def map_split(x):
    output = list(filter(None, map(lambda y: gen_split(y), x)))
    return output


for db in dbs:
    if len(db['ob']['name'].split(' ')) == 1:
        matches = str(subprocess.run(['pip', 'search', db['ob']['name']], stdout=subprocess.PIPE).stdout)
        if len(matches) > 3:
            get_match = map_split(matches.split("\\n"))
            appender = { 'database': db['ob'], 'matches': get_match }
            url.append(appender)
        print(db['ob']['name'])

with open('data/db_pip.json', 'w') as f:
    dump(url, f)



map(gen_split, url)

aa = re.search("(.*?)\s*-\s(.*)", str(url[1]['matches'][0]))
