from re import search, sub
import json


def goodHit(query, text):
    """Check for expected query call in file content.

    Parameters
    ----------
    query : str
        Text string passed to the original GitHub code search query.
    text : list
        The File contents, including highlighted fragments.

    Returns
    -------
    type
        Description of returned object.

    """

    strings = query.split("\" \"")
    strings = map(lambda x: sub(r"\"", "", x), strings)
    strings = list(map(lambda x: sub(r"\/*\sin\:file", "", x), strings))
    check = []
    for substring in strings:
        checkname = list(map(lambda x: search(substring.lower(),
                                              x.get('fragment').lower()),
                             text))
        check = check + checkname
        check = checkname
    output = not(all(matches is None for matches in check))
    if output is not True:
        f = open("fail_log.txt", "a")
        textdump = {'query': query,
                    'text': list(map(lambda x: x.get('fragment'), text))}
        f.write(json.dumps(textdump) + "\n")
        f.close()
    else:
        f = open("pass_log.txt", "a")
        textdump = {'query': query,
                    'text': list(map(lambda x: x.get('fragment'), text))}
        f.write(json.dumps(textdump) + "\n")
        f.close()
    return output
