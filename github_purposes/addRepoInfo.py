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
import random
import requests
import re
import os
from github import Github


def checkRepo(obj):
    """Return repository information.
    obj A pyGithub ContentFile object.
    """
    textcontent = str(obj.get_readme().decoded_content)
    # The following regex matches badges:
    badges = len(re.findall(r'\[!\[.+?]\(.+?\)\]\(http.+?\)', textcontent))
    created = obj.created_at
    forks = obj.forks_count
    watchers = obj.watchers_count
    isFork = obj.fork
    return {'created': created,
            'badges': badges,
            'forks': forks,
            'fork': isFork,
            'watchers': watchers}


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

with open('./gh.token') as f:
    gh_token = f.read().splitlines()

g = Github(gh_token[2])

repolist = ['SimonGoring/neotoma', 'ropensci/neotoma', 'annaegeorge/AnnaEGeorge.github.io', 'WilliamsPaleoLab/Geography523']

repoupdates = {}

for i in repolist:
    repo = g.get_repo(i)
    forks = repo.forks_count
    watchers = repo.watchers_count
    readme = repo.get_readme()
