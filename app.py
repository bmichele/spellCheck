import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
# from gensim.models import FastText as fText
import data_cleaning







##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'nhs_unigram.csv'
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

VOCAB = data.values
VOCAB = {w: c for w, c in VOCAB}

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

@app.route('/<string:query>/_edit_distance', methods = ['GET'])
def get_similar(query: str) -> Response:
    '''
    Returns words with lower levenshtein distance from query word
    :param query:
    :param words:
    :return:
    '''
    w0 = list(VOCAB.keys())[0]
    d0 = levenshtein(query, w0)
    cand = [w0]
    for w in VOCAB:
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

@app.route('/<string:query>/_semantic_distance', methods = ['GET'])
def get_similar_sem(query: str) -> Response:
    '''
    Returns words with lower semantic distance from query word
    :param query:
    :param words:
    :return:
    '''
    dists = []
    for i, w in enumerate(VOCAB.keys()):
        #print(i, w)
        dists.append(my_distance(query, w))
    out = [(w, str(d)) for d, w in sorted(zip(dists, VOCAB.keys()))]
    return Response(json.dumps({'out': out[:10]}),
                    status = 200,
                    mimetype = 'application/json')

# TODO: use edit distance and store the most similar instead of just the words with lower distance. Then compute similarity using embedding or percentage on edit distance
# TODO: use data to evaluate different algorithms

@app.route('/<string:query>', methods = ['GET'])
def get_candidates(query: str) -> Response:
    '''

    :param query:
    :return:
    '''
    out = candidates(query, VOCAB)
    # normalize scores so that sum up to one
    total = sum([c for _, c in out])
    out = {w: c/total for w, c in out}
    return Response(json.dumps({'candidates': out}),
                    status = 200,
                    mimetype = 'application/json')

########
# Main #
########

if __name__ == '__main__':
    # TODO: deactivate debug mode when done
    app.run(debug = True, host = '0.0.0.0')