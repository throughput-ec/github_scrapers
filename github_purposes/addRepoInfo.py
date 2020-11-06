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


def authorNames(author):
    """Pull author names from a set of commit authors."""
    author = author.author
    if author is not None:
        return author.login
    else:
        return None


def checkReadme(obj):
    """Check the README file for a repository."""
    try:
        readme = obj.get_readme()
        textcontent = str(readme.decoded_content)
        # The following regex matches badges:
        badges = len(re.findall(r'\[!\[.+?]\(.+?\)\]\(http.+?\)', textcontent))
        headings = len(re.findall(r'##+\s', textcontent))
        readme = {'readme': True,
                  'badges': badges,
                  'headings': headings,
                  'char': len(textcontent)}
    except Exception:
        readme = {'readme': False,
                  'badges': None,
                  'headings': None,
                  'char': None}
    try:
        license = obj.get_license().license.name
    except Exception:
        license = None
    return {'readme': readme, 'license': license}


def toString(dt):
    """Convert datetime object to string."""
    return dt.strftime("%Y-%m-%d (%H:%M:%S.%f)")


def checkRepo(obj):
    """Return repository information.

    obj A pyGithub ContentFile object.
    """
    created = toString(obj.created_at)
    # Check commit information:
    commits = obj.get_commits()
    commitCount = commits.totalCount
    description = obj.description
    lastCommit = toString(commits[0].commit.author.date)
    firstCommit = toString(commits[-1].commit.author.date)
    authors = set(map(lambda x: authorNames(x), commits))
    issues = obj.get_issues().totalCount
    branches = obj.get_branches().totalCount
    forks = obj.forks_count
    watchers = obj.watchers_count
    stars = obj.stargazers_count
    isFork = obj.fork
    languages = requests.get(obj.languages_url).json()
    return {'id': obj.id,
            'repo': obj.name,
            'owner': obj.owner.login,
            'name': obj.owner.login + '/' + obj.name,
            'url': obj.html_url,
            'created': created,
            'description': description,
            'topics': obj.get_topics(),
            'readme': checkReadme(obj),
            'commits': {'totalCommits': commitCount,
                        'range': [firstCommit, lastCommit],
                        'authors': list(authors)},
            'languages': languages,
            'stars': stars,
            'forks': forks,
            'fork': isFork,
            'issues': issues,
            'branches': branches,
            'watchers': watchers,
            'checkdate': toString(datetime.now())
            }


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

cypher = """
    MATCH (cr:codeRepo)
    WHERE NOT EXISTS(cr.meta)
    WITH cr, rand() AS random
    ORDER BY random DESC
    RETURN cr.url AS url
    SKIP $offset
    LIMIT 20
    """

add_meta = """
    MATCH (cr:codeRepo)
    WHERE cr.url = $url OR cr.id = $id
    SET cr.id = $id
    SET cr.meta = toString($meta)
    SET cr.url = $url
    SET cr.name = $name
    SET cr.status = NULL
    RETURN 'okay'
    """

add_dead = """
    MATCH (cr:codeRepo)
    WHERE cr.url = $url
    SET cr.status = 404
    RETURN 'okay'
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

repoupdates = []
skipped = []
val = 0

for j in offsets:
    repolist = graph.run(cypher, {'offset': j}).data()
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
        # testRepoName = i['cr']['name']
            try:
                repo = g.get_repo(ownerName + '/' + repoName)
            except RateLimitExceededException as e:
                print(e)
                left = g.get_rate_limit()
                resetPoint = (left.core.reset
                              - datetime.utcnow()).total_seconds()
                print('We need to wait ' + "{:.2f}".format(resetPoint)
                      + ' seconds until rate reset.')
                for ctd in range(int(resetPoint), 0, -30):
                    time.sleep(30)
                    resettime = (left.core.reset
                                 - datetime.now()).total_seconds() - 21600
                    print("{:.1f}".format(resettime)
                          + ' seconds until rate reset.')
                    if int(resettime) < 0:
                        break
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
                repoInfo = checkRepo(repo)
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
