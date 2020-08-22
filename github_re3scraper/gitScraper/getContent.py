def getContent(g, searchString):
    """Return GitHub search matches from query.

    Parameters
    ----------
    g : GitHub
        A GitHub connection.
    searchString : str
        A string to be passed to the GitHub code search.

    Returns
    -------
    ContentFile
        Description of returned object.

    """
    i = 0
    while True:
        try:
            content_files = g.search_code(query=searchString, highlight=True)
            hitRepos = content_files.totalCount
            print("   Returning " + str(content_files.totalCount) + " results.")
            break
        except RateLimitExceededException:
            delay = g.rate_limiting_resettime
            diff = delay - int(time.mktime(time.gmtime()))
            print("Hit error.  Waiting: 2mins")
            time.sleep(600)
            i = i + 1
            if i > 5:
                raise RuntimeError("Could not connect to GitHub.")

    return content_files
