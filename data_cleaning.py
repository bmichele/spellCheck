#################
# Data Cleaning #
#################

import pandas as pd
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from collections import Counter

# Helper functions
###################


def clean(x: str) -> str:
    '''
    Remove spaces and quotes from input string
    '''
    return x.replace(' ', '').replace('"', '')

def clean_message(sentence: str) -> list:
    '''
    Given a string containing a sentence, returns a list of clean tokens
    '''
    # TODO: install NLTK and tokenize with word tokenizer
    out = word_tokenize(sentence)
    out = [clean(w.lower()) for w in out if w]
    return out

# Medical corpus
#################

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
word_counts = [clean(el) for el in word_counts]

# split each word-count pairs on ':' and set proper type to counts
word_counts = [tuple(el.split(':')) for el in word_counts]
word_counts = [(w, int(c)) for w, c in word_counts]

# save the clean dataset to a csv file
df = pd.DataFrame(data = {'word': [w for w, _ in word_counts],
                          'count': [c for _, c in word_counts]})
df.to_csv(OUT_FILE, index = False)

# Symptoms corpus
##################

IN_FILE = 'data/health_queries.csv'
OUT_FILE = 'data/health_queries_clean.csv'

texts = pd.read_csv(IN_FILE).values

all_tokens = []
for text in texts:
    all_tokens.extend(clean_message(text[0]))
all_tokens = dict(Counter(all_tokens))

df = pd.DataFrame(data = {'word': [w for w, _ in all_tokens.items()],
                          'count': [c for _, c in all_tokens.items()]})
df.to_csv(OUT_FILE, index = False)