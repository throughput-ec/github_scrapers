import sys
from github import RateLimitExceededException
from gitScraper.callquery import callquery
from time import sleep


def tryCatchQuery(g, parent, query):
    k = 1
    while True:
        if k > 10:
            libcall = []
            break
        try:
            libcall = callquery(g, query)
            break
        except RateLimitExceededException:
            print("Unexpected error:", sys.exc_info()[0])
            print('Oops, broke for ' + parent
                  + ' with library call.')
            sleep(120)
            k = k + 1
            continue
        except Exception as inst:
            print("Unexpected error:", str(inst))
            print('Oops, broke for ' + parent
                  + ' with library call.')
            sleep(120)
            k = k + 1
            continue
    return libcall
