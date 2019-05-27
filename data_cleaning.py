#################
# Data Cleaning #
#################

import pandas as pd

IN_FILE = 'data/nhs_unigram.txt'
OUT_FILE = 'data/nhs_unigram.csv'

# load data
with open(IN_FILE, 'r+') as f:
     data = f.read()

# define lists for words and respective counts
words = []
counts = []
for el in data.split(','):
    el = el.split(':')
    words.append(el[0].strip().replace('"',''))
    counts.append(int(el[1].strip()))

del data

# save the clean dataset to a csv file
df = pd.DataFrame(data = {'word': words, 'count': counts})


df.to_csv(OUT_FILE, index = False)