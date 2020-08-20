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
from gitScraper.tryCatchQuery import tryCatchQuery
import time


def emptyNone(val):
    """Short summary.

    Parameters
    ----------
    val : dict
        Any dict, where None values exist.

    Returns
    -------
    dict
        An object that matches `val` with all None values
        replaced with empty strings.

    """
    for k in val.keys():
        if type(val[k]) is dict:
            emptyNone(val[k])
        else:
            if val[k] is None:
                val[k] = ''
    return val


good = False

with open('.gitignore') as gi:
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
cypher = """
    MATCH (:TYPE {type:"schema:CodeRepository"})<-[:isType]-(cr:OBJECT)
    MATCH (cr)-[:Target]-(:ANNOTATION)-[tar:Target]-(ot:OBJECT)
    MATCH (ot)-[:isType]->(:TYPE {type:"schema:Grant"})
    WITH COLLECT(DISTINCT ot.name) AS goodies
    MATCH (ob:OBJECT)-[:isType]-(:TYPE {type:"schema:Grant"})
    MATCH (ob)-[:Year_Started]->(y:Year)
    WHERE y.Year > 2015
    AND (NOT ob.name IN goodies)
    AND NOT EXISTS(ob.checked)
    RETURN DISTINCT ob
    """

print("Matching existing repositories")
dbs = graph.run(cypher).data()

random.shuffle(dbs)

for db in dbs:
    time.sleep(10)
    print("Running graphs for", db['ob']['name'])
    searchString = '"NSF ' + db['ob']['AwardID'] + '" in:file'
    repositories = set()
    content_files = list(tryCatchQuery(g, db['ob']['name'], searchString))
    if len(content_files) > 0:
        i = 0
        for cf in content_files:
            cf = loads(cf)
            repElem = {'ghid': cf.get('id'),
                       'ghurl': cf.get('url'),
                       'ghdescription': cf.get('description'),
                       'ghname': cf.get('name'),
                       'otid': db['ob']['AwardID']}
            repElem = emptyNone(repElem)
            connect = """MATCH (obb:OBJECT)
                         WHERE obb.AwardID = $otid
                         OPTIONAL MATCH (oba:OBJECT)
                         WHERE oba.id = $ghid
                         WITH oba, obb
                         OPTIONAL MATCH (oba)<-[:Target]-(a:ANNOTATION)-[:Target]->(obb)
                         RETURN oba, a, obb
                         """
            test = graph.run(connect, repElem).data()
            if test[0]['obb'] is not None and test[0]['a'] is None:
                i = i + 1
                print("    * Adding repository " + repElem['ghname']
                      + " to the graph.")
                with open('cql/github_linker.cql', mode="r") as gitadd:
                    silent = graph.run(gitadd.read(), repElem)
            else:
                addcheck = """MATCH (obb:OBJECT)
                              WHERE obb.AwardID = $otid
                              SET obb.checked = timestamp()"""
                silent = graph.run(addcheck, repElem)
    else:
        addcheck = """MATCH (obb:OBJECT)
                      WHERE obb.AwardID = $otid
                      SET obb.checked = timestamp()"""
        silent = graph.run(addcheck, repElem)
