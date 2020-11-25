import json
import pypandoc
import re

with open('readmes.json', 'r') as f:
    readmes = json.load(f)


def jsonPandoc(x):
    if x['t'] == 'Space':
        return ' '
    if x['t'] == 'SoftBreak':
        return '\n'
    if x['t'] == 'Link':
        return x['c'][1][0]['c']
    if x['t'] == 'Quoted':
        return '\''.join(list(map(lambda x: jsonPandoc(x['c']), input)))
    if x['t'] == 'DoubleQuote':
        return '\"'.join(list(map(lambda x: jsonPandoc(x['c']), input)))
    if x['t'] == 'Str':
        return x['c']
    else:
        return json.dumps(x['c'])


def reparsePandoc(input):
    return ''.join(list(map(lambda x: jsonPandoc(x), input)))


def parseJsonHeaders(parsed):
    doc = json.loads(parsed)['blocks']
    result = []
    order = 0
    for x in doc:
        if x['t'] == 'Header':
            result.append({'order': order,
                           'level': x['c'][0],
                           'header': reparsePandoc(x['c'][2])})
            order = order + 1
    return result


def splitDoc(input):
    parsed = pypandoc.convert_text(re.sub(r'\\n', r'\n', input), 'json', format='md')
    chunked = parseJsonHeaders(parsed)
    return chunked


output = []

for i in range(len(readmes)):
    print(i, end=' ', flush = True)
    object = readmes[i]['readme']
    if object is None:
        continue
    else:
        object = object[2:-1]
    doc = object.strip(' \\n')
    if len(doc) > 200000:
        continue
    parsed = {'repo': readmes[i]['repo'], 'sections':[]}
    try:
        parsed['sections'] = splitDoc(doc)
        output.append(parsed)
    except:
        print('oops.')
    if i % 100 == 0:
        print('Writing. . . ')
        with open('readmejson.json', 'a') as f:
            json.dump(output, f)
