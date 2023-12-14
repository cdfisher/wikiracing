"""get_redirect_target.py
Chris Fisher, 2023

Script to fetch the target page ID of a redirect via the MediaWiki
API in cases where an edge from redirect to target is not listed
in the source data. This appears to occur when a page was always a
redirect, and does not seem to occur when a page that previously had
other content is turned into a redirect.

Used in preprocess_sql_data.py to help ensure completeness of the
wiki graph.
"""
import requests

#API_URL = 'https://classic.runescape.wiki/api.php'
API_URL = 'https://oldschool.runescape.wiki/api.php'


def parse(page_id):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "rvlimit": 1,
        "pageids": page_id,
        "format": "json",
        "formatversion": "2",
        "redirects": 1
    }
    headers = {"User-Agent": "Contact: cdfisher on GitHub"}
    req = requests.get(API_URL, headers=headers, params=params)
    try:
        res = req.json()
        pagename = res["query"]["pages"][0]["pageid"]
        return pagename
    except requests.exceptions.JSONDecodeError:
        print(f'JSONDecodeError for ID {page_id}, \n{req}')
    except:
        print(f'Exception from ID {page_id}')
