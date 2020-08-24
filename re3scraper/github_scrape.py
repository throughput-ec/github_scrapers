#!/usr/bin/env python3
''' GitHub Python scraper

Linking to github repositories to find all repositories that contain code
related to the Re3Data databases.

This code hits the abuse detection mechanism, even with the pausing.
'''

from github import Github
from py2neo import Graph
from json import loads, load
import random
import re
from gitScraper.tryCatchQuery import tryCatchQuery


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

g = Github(gh_token[2])

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

for db in dbs:
    print("Running graphs for", db['ob']['name'])
    url = re.sub("http*://", '', db['ob']['url'])
    repositories = set()
    if len('"' + db['ob']['name'] + '" "' + url + '" in:file') > 127:
        searchString = '"' + db['ob']['name'] + '" in:file'
    else:
        searchString = '"' + db['ob']['name'] + '" "' + url + '" in:file'
    content_files = list(tryCatchQuery(g, db['ob']['name'], searchString))
    if len(content_files) > 0:
        i = 0
        total = len(content_files)
        for cf in content_files:
            cf = loads(cf)
            repElem = {'ghid': cf.get('id'),
                       'ghurl': cf.get('url'),
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
                print("    * Adding repository " + repElem['ghname'] + " to the graph.")
                with open('cql/github_linker.cql', mode="r") as gitadd:
                    silent = graph.run(gitadd.read(), repElem)
