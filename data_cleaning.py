#################
# Data Cleaning #
#################

import pandas as pd

IN_FILE = 'data/nhs_unigram.txt'
OUT_FILE = 'data/nhs_unigram.csv'

# load data
with open(IN_FILE, 'r+') as f:
     data = f.read()

# make sure that the format "word1" : count1, ..., "wordn": countn is uniform in the string
assert data.count('"') == 2 * data.count(':')
assert data.count(',') == data.count(':') - 1

# split word/count pairs splitting on commas
word_counts = data.split(',')
del data

# remove spaces (as there are ony unigrams) and quotes
def clean(x):
    return x.replace(' ', '').replace('"', '')
word_counts = [clean(el) for el in word_counts]

# split each word-count pairs on ':' and set proper type to counts
word_counts = [tuple(el.split(':')) for el in word_counts]
word_counts = [(w, int(c)) for w, c in word_counts]

# save the clean dataset to a csv file
df = pd.DataFrame(data = {'word': [w for w, _ in word_counts],
                          'count': [c for _, c in word_counts]})
df.to_csv(OUT_FILE, index = False)