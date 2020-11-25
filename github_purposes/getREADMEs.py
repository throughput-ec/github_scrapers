"""GitHub Repository Data Collection.

Using repository information in Throughput, add additional data using the Github
API.  This data is part of the Github schema, and we'll follow that standard.

The Github repository API response is listed at https://docs.github.com/en/free-pro-team@latest/rest/reference/repos

Given this structure, we are most interested in the following properties:

[
  {
    "id": 1296269,
    "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "owner": {
      "login": "octocat",
      "id": 1,
    },
    "private": false,
    "html_url": "https://github.com/octocat/Hello-World",
    "description": "This your first repo!",
    "fork": false,
    "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
    "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
    "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
    "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
    "language": null,
    "forks_count": 9,
    "stargazers_count": 80,
    "watchers_count": 80,
    "size": 108,
    "default_branch": "master",
    "open_issues_count": 0,
    "is_template": true,
    "topics": [
      "octocat",
      "atom",
      "electron",
      "api"
    ],
    "has_issues": true,
    "has_projects": true,
    "has_wiki": true,
    "has_pages": false,
    "has_downloads": true,
    "archived": false,
    "disabled": false,
    "visibility": "public",
    "pushed_at": "2011-01-26T19:06:43Z",
    "created_at": "2011-01-26T19:01:12Z",
    "updated_at": "2011-01-26T19:14:43Z",
    "subscribers_count": 42,
    "network_count": 0,
    "license": {
      "key": "mit",
      "name": "MIT License",
      "spdx_id": "MIT",
      "url": "https://api.github.com/licenses/mit",
      "node_id": "MDc6TGljZW5zZW1pdA=="
    }
  }
]


This code hits the abuse detection mechanism, even with the pausing.
"""

from py2neo import Graph
import json
import requests
import re
import os
from github import Github, RateLimitExceededException
from datetime import datetime
import time


def checkReadme(obj):
    """Check the README file for a repository."""
    try:
        readme = obj.get_readme()
        textcontent = str(readme.decoded_content)
    except Exception:
        textcontent = None
    return {'repo': obj.full_name, 'readme': textcontent}


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

graph = Graph(**data)

tx = graph.begin()

cypherES = """
    MATCH (kw:KEYWORD)
    WHERE kw.keyword CONTAINS('earth') OR kw.keyword CONTAINS('paleo')
    WITH kw
    MATCH (db:dataCat)<-[:Body]-(:ANNOTATION)-[:hasKeyword]->(kw)
    WITH db
    MATCH (cr:codeRepo)<-[:Target]-(:ANNOTATION)-[:Target]->(db)
    WITH DISTINCT cr.id AS id, cr.url AS url, db.name AS name, rand() AS random
    ORDER BY random
    RETURN id, url
    SKIP toInteger($offset)
    LIMIT 20
    """

cypherAll = """
    MATCH (cr:codeRepo)
    WHERE NOT EXISTS(cr.meta)
    WITH DISTINCT cr.id AS id, cr.url AS url, rand() AS random
    ORDER BY random
    RETURN id, url
    SKIP toInteger($offset)
    LIMIT 20
    """

cypher_count = """
    MATCH (cr:codeRepo)
    WHERE NOT (EXISTS(cr.meta) OR EXISTS(cr.status))
    RETURN COUNT(DISTINCT cr) AS total
    """

print("Matching existing repositories")
total_repos = graph.run(cypher_count).data()[0]['total']

offsets = range(0, total_repos, 20)

with open('./gh.token') as f:
    gh_token = f.read().splitlines()

g = Github(gh_token[2])

with open('readmes.json', 'r') as f:
    readmes = json.load(f)

repoupdates = []
skipped = []
val = 0

for j in offsets:
    with open('readmes.json', 'w') as f:
        json.dump(readmes, f)
    repolist = graph.run(cypherES, {'offset': j}).data()
    if len(repolist) < 20:
        repolist = graph.run(cypherAll, {'offset': j}).data()
    print(str(val) + ' of ' + str(total_repos))
    for i in repolist:
        val = val + 1
        url = i['url'].split('/')
        try:
            repoIdx = url.index('github.com')
        except ValueError:
            continue
        if len(url) > repoIdx + 2:
            ownerName = url[repoIdx + 1]
            repoName = url[repoIdx + 2]
            if (ownerName + '/' + repoName) in [k['repo'] for k in readmes]:
                continue
            try:
                repo = g.get_repo(ownerName + '/' + repoName)
            except RateLimitExceededException as e:
                print(e)
                left = g.get_rate_limit()
                currentUTC = datetime.utcnow()
                currenthome = datetime.now()
                print('Hit rate limit at '
                      + currenthome.strftime("%m/%d/%Y, %H:%M:%S"))
                resetPoint = (left.core.reset
                              - currentUTC).total_seconds()
                print('We need to wait ' + "{:.2f}".format(resetPoint/60)
                      + ' minutes until rate reset.')
                for wait in range(int(resetPoint) + 60):
                    time.sleep(1)
                    if (wait % 60) == 0:
                        print('.', end="")
                print('Ended wait at '
                      + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            except Exception as e:
                print(e)
                # If we don't get the right repository, we can check to see
                # if there's a near match for the repository name.  That's
                # because the regex for DeepDive was a bit rough.
                try:
                    user = g.get_user(ownerName)
                    repoSet = user.get_repos()
                    repoNames = list(map(lambda x: x.name, repoSet))
                    indices = [k for k,
                               s in enumerate(repoNames) if repoName in s]
                    if len(indices) > 0:
                        repo = g.get_repo(ownerName + '/' + indices[0])
                    else:
                        # We got a 404 and couldn't find anything matching.
                        print('Hit a 404 for ' + i['url'])
                        continue
                except Exception:
                    print('Hit a 404 for ' + i['url'])
                    continue
            try:
                readmes.append(checkReadme(repo))
                print(i['url'])
            except Exception as e:
                print(e)
                skipped.append(i['url'])
                print('Couldn\'t get readme for ' + i['url'])
