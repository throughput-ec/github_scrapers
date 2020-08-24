import sys
from github import RateLimitExceededException
from gitScraper.callquery import callquery
from time import sleep


def tryCatchQuery(g, parent, query):
    while True:
        try:
            libcall = callquery(g, query)
            break
        except RateLimitExceededException:
            print("Unexpected error:", sys.exc_info()[0])
            print('Oops, broke for ' + parent
                  + ' with library call.')
            sleep(120)
            continue
        except Exception as inst:
            print("Unexpected error:", str(inst))
            print('Oops, broke for ' + parent
                  + ' with library call.')
            sleep(120)
            continue
    return libcall
