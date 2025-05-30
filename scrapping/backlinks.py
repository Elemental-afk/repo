import requests
import time

url = "https://en.wikipedia.org/w/api.php"
params = {
    "action": "query",
    "format": "json",
    "list": "backlinks",
    "bltitle": "Adrian_Zandberg",
    "bllimit": "max"
}

response = requests.get(url, params=params).json()
backlinks = [pg["title"] for pg in response["query"]["backlinks"]]

normalpages = []
for page in backlinks:
    if page.startswith("User:") or page.startswith("Wikipedia:") or page.startswith("File:") or page.startswith("Template:"):
        continue
    normalpages.append(page)

print(len(normalpages), "pages found linking to Adrian Zandberg.")
print("Pages linking to Adrian Zandberg:", normalpages)


newnormalpages = set()
for pagename in normalpages:
    params = {
        "action": "query",
        "format": "json",
        "list": "backlinks",
        "bltitle": pagename,
        "bllimit": "max"
    }
    time.sleep(1)  #rate limiting
    response = requests.get(url, params=params).json()
    backlinks = [pg["title"] for pg in response["query"]["backlinks"]]
    for page in backlinks:
        if page.startswith("User:") or page.startswith("Wikipedia:") or page.startswith("File:") or page.startswith("Template:"):
            continue
        newnormalpages.add(page)

print(len(newnormalpages), "pages found linking to Adrian Zandberg.")
print("Pages linking to Adrian Zandberg:", newnormalpages)

import json
with open("backlinks.json", "w") as f:
    json.dump(list(newnormalpages), f, indent=4)

