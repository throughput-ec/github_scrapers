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
import github3
from datetime import datetime
import time
from gitscraper import checkRepo


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

graph = Graph(**data)

tx = graph.begin()


add_meta = open('./cql/addMeta.cql').read()
cypherAll = open('./cql/cypherAll.cql').read()
add_dead = open('./cql/addDead.cql').read()
cypher_count = open('./cql/cypherCount.cql').read()
cypherES = open('./cql/earthsciCypher.cql').read()

print("Matching existing repositories")
total_repos = graph.run(cypher_count).data()[0]['total']

offsets = range(0, total_repos, 20)

# Here's the login for GitHub:
with open('./throughput-data-loader.2021-05-04.private-key.pem') as f:
    pemfile = f.read()

g = github3.github.GitHub()
g.login_as_app(pemfile.encode(), '32829')
installations = [installation.id for installation in g.app_installations()]
g.login_as_app_installation(pemfile.encode(), '32829', installations[0])

# Back to the rest.

repoupdates = []
skipped = []
val = 0

for j in offsets:
    repolist = graph.run(cypherAll, {'offset': j}).data()
    if len(repolist) == 0:
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
            try:
                repo = g.repository(ownerName, repoName)
            except github3.exceptions.AppInstallationTokenExpired as e:
                g = github3.github.GitHub()
                g.login_as_app(pemfile.encode(), '32829')
                installations = [installation.id for installation in g.app_installations()]
                g.login_as_app_installation(pemfile.encode(), '32829', installations[0])
            # except RateLimitExceededException as e:
            #     print(e)
            #     left = g.get_rate_limit()
            #     currentUTC = datetime.utcnow()
            #     currenthome = datetime.now()
            #     print('Hit rate limit at '
            #           + currenthome.strftime("%m/%d/%Y, %H:%M:%S"))
            #     resetPoint = (left.core.reset
            #                   - currentUTC).total_seconds()
            #     print('We need to wait ' + "{:.2f}".format(resetPoint/60)
            #           + ' minutes (' + "{:.0f}".format(resetPoint) + 's) until rate reset.')
            #     for wait in range(int(resetPoint) + 60):
            #         time.sleep(1)
            #         if (wait % 60) == 0:
            #             print(str(wait) + '.', end="", flush=True)
            #     print('Ended wait at '
            #           + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
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
                        bb = graph.run(add_dead, {'url': i['url']})
                        print('Hit a 404 for ' + i['url'])
                        continue
                except Exception:
                    bb = graph.run(add_dead, {'url': i['url']})
                    print('Hit a 404 for ' + i['url'])
                    continue
            try:
                repoInfo = checkRepo.checkRepo(repo)
                repoupdates.append(repoInfo)
                uploadObj = {'meta': json.dumps(repoInfo),
                             'id': repoInfo['id'],
                             'name': repoInfo['name'],
                             'url': repoInfo['url']}
                aa = graph.run(add_meta, uploadObj)
                print(i['url'])
            except Exception as e:
                print(e)
                skipped.append(i['url'])
                print('Couldn\'t upload for ' + i['url'])
