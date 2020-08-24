[![lifecycle](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)
[![NSF-1928366](https://img.shields.io/badge/NSF-1928366-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1928366)

# Throughput GitHub Scrapers

The [Throughput Database](http://throughputdb.com) was seeded with information obtained from scraping GitHub using an authorized script.  The scrapers looked for both repositories associated with specific NSF Awards, and also with databases defined within Re3Data.

These scripts connect to an instance of the Throughput Neo4j graph database (using the py2neo Pyhton package) and make calls to the GitHub API using the GitHub package ([pyGithub](https://pygithub.readthedocs.io/en/latest/index.html)) for Python.  With each query there are checkers to ensure that the script has not triggered that rate limiter, to ensure that the query is sucessfully returning information that is relevant to Throughput and valid for the award, and then to post the data to the Throughput Database.

Both the NSF scraper and the re3scraper return two files, one for positive matches and one for negative matches, to let us better assess the quality of the returned data.

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

  *  [Simon Goring](http://goring.org) [![orcid](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) or branches.

All products of the Throughput Annotation Project are licensed under an [MIT License](LICENSE) unless otherwise noted.

## How to use this repository

This project was developed to require both an instance of a Neo4j graph database, and to use [Python virtual environments](https://docs.python.org/3/tutorial/venv.html).  Future work may focus on the development of a Docker-ized workflow, but at present there are no plans to do so.

The required packages are located within the file `requirements.txt` in the root folder of each of the two scrapers.  The requirements were generated using the [`pipreqs`](https://pypi.org/project/pipreqs/) package for Python.

To start to use one of the scripts, begin by initializing a virtual environment:

```bash
python3 -m venv .
source ./bin/activate
```

### Workflow Overview

Each script links to a Neo4j database and queries a set of objects (NSF Awards, Databases).  This returns an array of objects that are to be looped through.

Each object is used as the basis of a specific query to the Github code search API.  The result is a set of repositories (or no result). In the case of no result, we continue to the next API call.  If repositories match, we test each to determine whether they are of use to Throughput.

### System Requirements

This project uses Python v3.7.6, and Neo4j v4.1.1.  Development was undertaken on a system using Linux Mint 20.

### Data Requirements

The project requires a version of the Throughput Database.  A recent snapshot is available here, or the database can be reconstructed (in part) using the code within the [throughputdb](http://github.com/throughput-ec/throughputdb) repository.

### Key Outputs

This project adds data directly to the local (or remote) neo4j database.  Two files are created during the execution of the script:

*  `pass_log.txt` - Records each repository that was returned through the GitHub API request and was added to the Throughput graph.
* `fail_log.txt` - Records each repository that was returned through the GitHub API request and was *not* added to the Throughput graph.

Both files return a single result per line, in JSON format:

```json
{"query": "\"NSF  1541002\" in:file", "text": [" Paleoecology Database and Neotoma data stewards. Work on this paper was supported by NSF Awards NSF-1541002, NSF-1550707 and NSF-1550707.\n\n# REFERENCES\n"]}
```

It is possible to quickly check how many results have passed or failed using the linux command line argument `wc -l pass_log.txt` which will return the number of lines in the file.

## Metrics

This project is evaluated along the following metrics:
  * Successful implementation of NSF Award Scraper
  * Successful implementation of Re3Data Scraper
  * Number of Github repositories added to the Throughput Database
  *
