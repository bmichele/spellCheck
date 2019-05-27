import time
import os
import os.path as path
import pandas as pd

#############
# Functions #
#############

def memoize(func):
    mem = {}

    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]

    return memoizer

@memoize
def levenshtein(s, t):
    if s == "":
        return len(t)
    if t == "":
        return len(s)
    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1

    res = min([levenshtein(s[:-1], t) + 1,
               levenshtein(s, t[:-1]) + 1,
               levenshtein(s[:-1], t[:-1]) + cost])
    return res

def minlevensthein(s, t):
    '''
    Returns lower bound for levenshtein distance between s and t
    '''
    return abs(len(s) - len(t))
##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'nhs_unigram.csv'
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

# get most similar word to query
query = 'tempo'
words = data['word'].values
counts = data['count'].values
d0 = levenshtein(query, '')
cand = [] # list of candidate words

t0 = time.time()
for i, w in enumerate(words):
    if i % 1000 == 0: print(i)
    if minlevensthein(query, w) > d0:
        continue
    else:
        d = levenshtein(query, w)
        if d < d0:
            cand = [w]
        elif d == d0:
            cand.append(w)

print(time.time() - t0)