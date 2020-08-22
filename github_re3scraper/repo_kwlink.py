#!/usr/bin/env python3
''' GitHub Python scraper

Linking github repositories to their keywords/topics.

This code hits the abuse detection mechanism, even with the pausing.
'''

from github import Github
from github import RateLimitExceededException
from github.GithubException import UnknownObjectException
from py2neo import Graph
from json import load
import random
from time import sleep

with open('.gitignore') as gi:
    good = False
    # This simply checks to see if you have a connection string in your repo.
    # I use `strip` to remove whitespace/newlines.
    for line in gi:
        if line.strip() == "connect_remote.json":
            good = True
            break

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

cypher = """MATCH (:TYPE {type:"schema:CodeRepository"})-[:isType]-(cr:OBJECT)
            WHERE NOT EXISTS(cr.errorType)
            OPTIONAL MATCH (cr)-[]-(:ANNOTATION)-[]-(k:KEYWORD)
            WITH DISTINCT cr.name AS repos, k.keyword AS kw
            WHERE kw IS NULL
            RETURN repos;"""

print("Matching existing repositories")
dbs = graph.run(cypher).data()

random.shuffle(dbs)

short_db = dbs

for db in dbs:
    print(db['repos'])
    k = 0
    while True:
        sleep(2)
        if k > 10:
            break
        try:
            repo = g.get_repo(db['repos'])
            repo_top = repo.get_topics()
            if len(repo_top) > 0:
                print("Hitting a new repository with topics! -", repo.name)
                print(repo_top)
                addFiles = {'id': repo.id, 'keywords': repo_top}
                with open('cql/github_topics.cql', mode="r") as gitadd:
                    silent = graph.run(gitadd.read(), addFiles)
            silent = short_db.pop(short_db.index(db))
            break
        except UnknownObjectException as inst:
            print("Missing repo:", str(inst))
            with open('cql/repo404.cql', mode="r") as gitadd:
                silent = graph.run(gitadd.read(), db)
            print("Marked node.")
            break
        except RateLimitExceededException as inst:
            print("Rate exceeded:", str(inst))
            print('Oops, broke for ' + db['repos']
                  + ' with repo call.')
            sleep(300)
            k = k + 1
            continue
        except Exception as inst:
            print(inst)
            if inst['message'] = "Repository access blocked":
                break
            sleep(120)
            k = k + 1
            continue
