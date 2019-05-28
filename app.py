import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json

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


##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'nhs_unigram.csv'
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

WORDS = data['word'].values
# counts = data['count'].values

#################
# API functions #
#################


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def hello_world():
    return Response('Flask is running', status = 200)

@app.route('/<string:query>')
def get_similar(query: str) -> list:
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
        if minlevensthein(query, w) > d0:
            continue
        else:
            d = levenshtein(query, w)
            if d < d0:
                d0 = d
                cand = [w]
            elif d == d0:
                cand.append(w)
    out = {'edit_distance': d0,
           'candidates': cand}
    return Response(json.dumps(out),
                    status = 200,
                    mimetype = 'application/json')


########
# Main #
########

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')