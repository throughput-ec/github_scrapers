"""GitHub Python scraper.

Linking to github repositories to find all repositories that contain code
related to the Re3Data databases.

This code hits the abuse detection mechanism, even with the pausing.
"""

from py2neo import Graph
import json
import requests
import re
import os


def repotest(string):
    """Check to see if a repository is referenced in the paper.

    string A character string returned from geodeepdive highlights.
    returns None or the string matched.
    """
    test = re.search(r'((github)|(gitlab)|(bitbucket)).com\/((\s{0,1})[\w,\-,\_]+\/*){1,2}', string)
    if test is None:
        output = {'repo': None, 'highlight': string}
    else:
        output = {'repo': test[0].replace(' ', ''), 'highlight': string}
    return output


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

if os.path.exists('data/papersout.json'):
    with open('data/papersout.json', 'r') as file:
        paperset = json.load(file)
else:
    paperset = {'good': {}, 'bad': {}}

thing = 0
maxhits = 0
# This will generate a large-ish number of papers and grants.

gddurl = "https://geodeepdive.org/api/snippets?term=gitlab.com,bitbucket.com,github.com&clean&full_results"
hits = True
paperCt = 0

while hits:
    with open('data/papersout.json', 'w') as file:
        json.dump(paperset, file)
    print('Have run ' + str(paperCt) + ' papers, looking for ' + str(maxhits))
    results = requests.get(gddurl)
    if results.status_code == 200:
        output = results.json()
        gddurl = output['success']['next_page']
        maxhits = output['success']['hits']
        if len(output['success']['data']) > 0:
            data = output['success']['data']
            for papers in data:
                print("Running " + papers['doi'])
                repohits = map(lambda x: repotest(x), papers['highlight'])
                repohit = list(repohits)
                if any(repohit):
                    for hit in repohit:
                        if hit is not None:
                            if hit['repo'] in paperset['good']:
                                paperset['good'][hit['repo']
                                                 ]['papers'].append(papers)
                            else:
                                paperset['good'][hit['repo']] = {'url': hit['repo'],
                                                                 'papers': [papers]}
                else:
                    paperset['bad'][papers['doi']] = papers
                paperCt = paperCt + 1

good_list = [i for i in paperset['good'].values()]

for rec in good_list:
    if rec['url'] is None:
        paperset['bad'] = rec
        paperset['good'].remove(rec)
    else:
        rec['url'] = 'http://' + rec['url']

with open('data/papersout.json', 'w') as file:
    json.dump(paperset, file)

with open('data/papersgood.json', 'r') as file:
    good_list = json.load(file)

    json.dump(good_list, file)


# Connect to the graph database
if os.path.exists('./connect_remote.json'):
    with open('./connect_remote.json') as f:
        data = json.load(f)
else:
    raise Exception("No connection file exists.")

graph = Graph(**data)

tx = graph.begin()

# Link the papers to the github repositories:
k = 0
for i in good_list:
    k = k + 1
    if i['url'] is not None:
        i['url'] = re.sub(r'^g', 'https://g', i['url'])
        i['url'] = re.sub(r'^http:', 'https:', i['url'])
        i['url'] = re.sub(r'^https://https://github',
                          'https://github', i['url'])
        for j in i['papers']:
            dumper = {'ghurl': i['url'],
                      'doi': j['doi'],
                      'journal': j['pubname'],
                      'authors': j['authors'],
                      'pubname': j['title'],
                      'pprurl': j['URL'],
                      'title': j['title'],
                      'highlight': j['highlight']}
            print(str(k) + ": Running for " + i['url'] + " . . . ", end = '')
            with open("cql/checklinker.cql") as checker:
                checker = graph.run(checker.read(), dumper).data()
            if checker[0]['res'] == 0:
                print('Adding')
                with open("cql/addgitpaper.cql") as linker:
                    silent = graph.run(linker.read(), dumper)
            else:
                print('Already present.')
