[![lifecycle](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)
[![NSF-1928366](https://img.shields.io/badge/NSF-1928366-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1928366)

# Throughput Re3Data Github Scraper

A project to crawl data repositories in the Re3Data Data Archive and to then search for GitHub repositories that are linked to each of these databases.

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

  * [Simon Goring](http://goring.org) [![orcid](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks]() or branches.

All products of the Throughput Annotation Project are licensed under an [MIT License](LICENSE) unless otherwise noted.

## How to use this repository

This repository contains a Python script ([github_scrape.py]()), a bash script to help manage the abuse detection mechanism for GitHub. The repository does not contain the following files (which must be supplied by the user):

  * `connect_remote.json`: A connection file for the neo4j installation.
  * `gh.token`: A GitHub token for use with the GitHub API.

### Workflow Overview

Th project uses X core information, manages it and passes our some stuff.

### System Requirements

This project is developed using (Python? R?).  It runs on a Windows system (?).  Continuous integration uses TravisCI (?).

### Data Requirements

The project pulls data from Re3Data and GitHub using the GitHub API and Re3Data as linked through the Throughput Database.

### Key Outputs

This project generates (an API, some log files, what?)

## Metrics

This project is to be evaluated using the following metrics. . .
