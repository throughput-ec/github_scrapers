"""GitHub Python scraper.

Linking to github repositories to find all repositories that contain code
related to the Re3Data databases.

This code hits the abuse detection mechanism, even with the pausing.
"""

from py2neo import Graph
import json
import random
import requests
import re
import os


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

if os.path.exists('./connect_remote.json'):
    with open('./connect_remote.json') as f:
        data = json.load(f)
else:
    raise Exception("No connection file exists.")

if os.path.exists('data/papersout.json'):
    with open('data/papersout.json', 'r') as file:
        paperset = json.load(file)
else:
    paperset = {'good': [], 'bad': []}

awards = list(map(lambda x: x['AwardID'], paperset['good']))
awards.extend(list(map(lambda x: x['AwardID'], paperset['bad'])))

graph = Graph(**data)

tx = graph.begin()

cypher = """
    MATCH (:TYPE {type:"schema:Grant"})<-[:isType]-(gt:OBJECT)
    RETURN COUNT(DISTINCT gt) AS tot"""

grant_tot = graph.run(cypher).data()

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
grantUnlinked = list(map(lambda x: x['award'], grants))

grants = set(grantUnlinked) - set(awards)
grants = list(grants)

print("Matching " + str(len(grants)) + " of " +
      str(grant_tot[0]['tot']) + " research awards.")

thing = 0
maxhits = 0
# This will generate a large-ish number of papers and grants.

for grantno in grants:
    thing = thing + 1
    if thing % 1000 == 0:
        with open('data/papersout.json', 'w') as file:
            json.dump(paperset, file)
    print("Running graphs for", grantno)
    papers = set()
    gddurl = "https://geodeepdive.org/api/snippets?term=" + \
        grantno + "&clean&full_results"
    results = requests.get(gddurl)
    if results.status_code == 200:
        output = results.json()
        if output['success']['hits'] > 0:
            if output['success']['hits'] > maxhits:
                maxhits = output['success']['hits']
            print('got ' + str(output['success']['hits']) + ' hits')
            total = output['success']['hits']
            data = output['success']['data']
            for papers in data:
                papers['AwardID'] = grantno
                paperhits = map(lambda x: re.search(
                    '(NSF)|(nsf)|([Ss]ci.*[Ff]oun)', x) is not None,
                    {x for x in papers['highlight']})
                if any(list(paperhits)):
                    print('Good results')
                    paperset['good'].append(papers)
                else:
                    paperset['bad'].append(papers)

with open('data/papersout.json', 'w') as file:
    json.dump(paperset, file)

with open('data/papersgood.json', 'w') as file:
    json.dump(paperset['good'], file)
