
def toString(dt):
    """Convert datetime object to string."""
    return dt.strftime("%Y-%m-%d (%H:%M:%S.%f)")


def checkReadme(obj):
    """Check the README file for a repository."""
    try:
        readme = obj.readme()
        textcontent = str(readme.decoded)
        # The following regex matches badges:
        badges = len(re.findall(r'\[!\[.+?]\(.+?\)\]\(http.+?\)', textcontent))
        headings = len(re.findall(r'##+\s', textcontent))
        readme = {'readme': True,
                  'badges': badges,
                  'headings': headings,
                  'char': len(textcontent)}
    except Exception:
        readme = {'readme': False,
                  'badges': None,
                  'headings': None,
                  'char': None}
    try:
        license = obj.license().license.name
    except Exception:
        license = None
    return {'readme': readme, 'license': license}
