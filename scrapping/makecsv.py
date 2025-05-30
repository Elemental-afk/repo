import json
from pathlib import Path
import string
import shutil
import os
import pandas as pd

with open('/home/dominik/Documents/coding/mowinit/lab6/scwapping/titles.json') as f:
    sett = set(json.load(f))

res = list(filter(lambda x: all(y not in ":" for y in x), sett))
print(len(res))

files_extracted = []
for dirpath, _, filenames in os.walk("/home/dominik/Documents/coding/mowinit/lab6/scwapping/extracted/"):
    for filename in filenames:
        files_extracted.append(os.path.join(dirpath, filename))

i = 0
lang_text = []
final_matches = pd.DataFrame()

for _file in files_extracted:
    i += 1
    with open(_file, 'r') as f:
        file_lines = f.readlines() 
    for line in file_lines:
        lang_text.append(json.loads(line))
    if i % 1000 == 0:
        print(f"Processed {i} files")
        df = pd.DataFrame(lang_text)
        matches = df[df['title'].isin(set(res))]
        final_matches = pd.concat([final_matches, matches], ignore_index=True)
        lang_text = []


print(final_matches.shape)
print(final_matches.head())
final_matches.to_csv("zand_text.csv", index=False)
