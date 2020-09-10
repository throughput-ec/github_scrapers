"""GitHub Python scraper.

Linking to github repositories to find all repositories that contain code
related to the Re3Data databases.

This code hits the abuse detection mechanism, even with the pausing.
"""

from py2neo import Graph
from json import loads, load
import random
import requests
import re

def emptyNone(val):
    """Clean out None values.

    val A Python object that may or may not have None values.
    returns a Python object with all None values replaced by ''.
    """
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

graph = Graph(**data)

tx = graph.begin()

# The use of the >>>!!!<<< is used to show deprecation apparently.
# This returns 2255 research databases from re3data.
#  Here we're matching repos that have not been matched yet.
cypher = """
    MATCH (:TYPE {type:"schema:Grant"})<-[:isType]-(gt:OBJECT)
    MATCH (oa:OBJECT)-[:isType]->(:TYPE {type:"schema:Article"})
    MATCH (gt)-[:Target]-(:ANNOTATION)-[tar:Target]-(oa)
    WITH COLLECT(DISTINCT gt.name) AS goodies
    MATCH (gt:OBJECT)-[:isType]->(:TYPE {type:"schema:Grant"})
    WHERE (NOT gt.name IN goodies)
    RETURN DISTINCT gt.AwardID AS award"""

print("Matching existing repositories")
grants = graph.run(cypher).data()

random.shuffle(grants)
grants = list(map(lambda x: x['award'], grants))

for grantno in grants:
    print("Running graphs for", grantno)
    papers = set()

    gddurl = "https://geodeepdive.org/api/snippets?term=" + grantno + "&clean&full_results"

    results = requests.get(gddurl)
    if results.status_code == 200:
        output = results.json()
        total = output['success']['hits']
        data = output['success']['data']

        for papers in data:
            map(lambda x: re.search('(NSF)|(Nat.*Sci.*Foun)' is None, x),
                papers['highlights'])


    if len(content_files) > 0:
        i = 0
        total = len(content_files)
        for cf in content_files:
            cf = loads(cf)
            repElem = {'awardid': grantno,
                       'doi': cf.get('url'),
                       'ghdescription': cf.get('description'),
                       'ghname': cf.get('name'),
                       'otid': db['ob']['id']}
            repElem = emptyNone(repElem)
            connect = """MATCH (oba:OBJECT)
                         WHERE oba.id = $ghid
                         MATCH (obb:OBJECT)
                         WHERE obb.id = $otid
                         WITH oba, obb
                         MATCH (oba)<-[:Target]-(a:ANNOTATION)-[:Target]->(obb)
                         RETURN a
                         """
            test = graph.run(connect, repElem)
            if len(test.data()) == 0:
                i = i + 1
                print("    * Adding repository " + repElem['ghname']
                      + " to the graph.")
                with open('cql/github_linker.cql', mode="r") as gitadd:
                    silent = graph.run(gitadd.read(), repElem)
