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

def get_similar(query: str, words: list) -> list:
    '''
    Returns words with lower levenshtein distance from query word
    :param query:
    :param words:
    :return:
    '''
    w0 = words[0]
    d0 = levenshtein(query, w0)
    cand = [w0]
    for w in words:
        if minlevensthein(query, w) > d0:
            continue
        else:
            d = levenshtein(query, w)
            if d < d0:
                d0 = d
                cand = [w]
                print(d)
            elif d == d0:
                cand.append(w)
    return cand

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

t0 = time.time()
out = get_similar(query, words)
print(time.time() - t0)
print(out)