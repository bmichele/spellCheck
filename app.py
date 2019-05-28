import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
# from gensim.models import FastText as fText

####################
# Helper Functions #
####################

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

def get_ngrams(word, nmin, nmax):
    out = []
    l = len(word)
    for i in range(nmin - 1, nmax):
        #print('i', i)
        if i >= l:
            out.append(word)
            break
        else:
            for j in range(0, l - i):
                #print('Adding', word[j:j + i + 1])
                out.append(word[j:j+i+1])
    return out

def get_vector(word, nmin, nmax = 20):
    try:
        return EMBEDDING[word]
    except KeyError:
        ngrams = [el for el in get_ngrams(word, nmin, nmax) if el in EMBEDDING.vocab]
        if ngrams:
            return EMBEDDING[ngrams].sum(axis = 0)
        else:
            return np.zeros(300, dtype = 'float32')

def my_distance(word1, word2):
    #lmin = max(min(len(word1), len(word2)) - 1, 1)
    lmin = 2
    v1, v2 = get_vector(word1, nmin = lmin), get_vector(word2, nmin = lmin)
    return np.sqrt(np.power(v1 - v2, 2).sum())


##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'nhs_unigram.csv'
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

WORDS = data['word'].values
WORDS = [w.replace('"','').replace("'",'') for w in WORDS]
WORDS = {*[w for w in WORDS if w]}
WORDS = list(WORDS)
# counts = data['count'].values

##########################
# Loading FastText model #
##########################

print('Loading embeddings')
#EMBEDDING = KeyedVectors.load_word2vec_format("./models/wiki-news-300d-1M-subword.vec",binary=False)
EMBEDDING = KeyedVectors.load("./models/wiki-news-300d-1M-subword_keyedVectors")


#################
# API functions #
#################


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def hello_world():
    return Response('Flask is running', status = 200)

@app.route('/<string:query>/_edit_distance')
def get_similar(query: str) -> Response:
    '''
    Returns words with lower levenshtein distance from query word
    :param query:
    :param words:
    :return:
    '''
    w0 = WORDS[0]
    d0 = levenshtein(query, w0)
    cand = [w0]
    for w in WORDS:
        if d0 == 0:
            break
        if minlevensthein(query, w) > d0:
            continue
        else:
            d = levenshtein(query, w)
            if d < d0:
                d0 = d
                cand = [w]
            elif d == d0:
                cand.append(w)

    #out = {el: EMBEDDING.wv.similarity(query, el) for el in cand}
    out = {'edit_distance': d0,
           'candidates': cand}
    return Response(json.dumps(out),
                    status = 200,
                    mimetype = 'application/json')

@app.route('/<string:query>/_semantic_distance')
def get_similar_sem(query: str) -> Response:
    '''
    Returns words with lower semantic distance from query word
    :param query:
    :param words:
    :return:
    '''
    dists = []
    for i, w in enumerate(WORDS):
        #print(i, w)
        dists.append(my_distance(query, w))
    out = [(w, str(d)) for d, w in sorted(zip(dists, WORDS))]
    return Response(json.dumps({'out': out[:10]}),
                    status = 200,
                    mimetype = 'application/json')

########
# Main #
########

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')