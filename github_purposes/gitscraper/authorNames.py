def authorNames(author):
    """Pull author names from a set of commit authors."""
    author = author.author
    if author is not None:
        return author.login
    else:
        return None
