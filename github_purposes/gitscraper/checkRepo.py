import json
from datetime import datetime


def authorNames(author):
    """Pull author names from a set of commit authors."""
    author = author.author
    if author is not None:
        return author.login
    else:
        return None


def toString(dt):
    """Convert datetime object to string."""
    return dt.strftime("%Y-%m-%d (%H:%M:%S.%f)")


def checkReadme(obj):
    """Check the README file for a repository."""
    try:
        readme = obj.readme()
        textcontent = str(readme.decoded)
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
        license = obj.license().license.name
    except Exception:
        license = None
    return {'readme': readme, 'license': license}


def checkRepo(obj):
    """Return repository information.

    obj A pyGithub ContentFile object.
    """
    created = toString(obj.created_at)
    # Check commit information:
    commits = [i for i in obj.commits()]
    commitCount = sum(obj.weekly_commit_count()['all'])
    description = obj.description
    lastCommit = toString(obj.pushed_at)
    firstCommit = toString(obj.created_at)
    authors = set(map(lambda x: authorNames(x), commits))
    issues = obj.open_issues
    branches = len([i for i in obj.branches()])
    forks = obj.forks_count
    watchers = obj.watchers_count
    stars = obj.stargazers_count
    isFork = obj.fork
    languages = json.dumps([{i[0]:i[1]} for i in obj.languages()])
    return {'id': obj.id,
            'repo': obj.name,
            'owner': obj.owner.login,
            'name': obj.owner.login + '/' + obj.name,
            'url': obj.html_url,
            'created': created,
            'description': description,
            'topics': obj.topics().names,
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
