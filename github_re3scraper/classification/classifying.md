# Classifying GitHub Repositories

Currently, when Throughput returns GitHub repositories that are returned from a search it returns a list that is only ordered based on the number of databases any individual GitHub repository links to.  In general this is fine, but only just.  The utility of this service depends on being able to return useful links to individuals.

Given that, we can see clear differences in the types of repositories that are returned from searches.  Some repositories are worked assignments by students or people learning how to code.  There are other important metrics or elements for a repository, for example, a README file, the language the code is written in, the number of commits, and the date since the last commit.

Some of these we can pull from GitHub using the github Python package:

Last commit:

```python
from github import Github
g = Github("username","password")

repo = g.get_repo("user/repo")
commits = g.get_repo("user/repo").get_commits()
dates = set()
for i in commits:
  dates.add(i.commit.author.date)
mostRecent = max(dates)
```

Total commits:

``` python
from github import Github
g = Github("username","password")
counts = g.get_repo("user/repo").get_commits().totalCount
```

Unique Authors:

``` python
from github import Github
g = Github("username","password")
commits = g.get_repo("SimonGoring/simongoring.github.io").get_commits()
name = set()
for i in commits:
  name.add(i.author)

len(name)
```
