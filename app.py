import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json
from spellCheck import NorvigCheck, EditDistanceCheck, SemanticCheck
from utilities import download_embeddings
from gensim.models import FastText as fText
import logging
logging.basicConfig(#filename='example.log',
                    level=logging.DEBUG)

# TODO: run benchmarks and report output in readme file (see 'Test' section)

###################################################
# Read environment variables defined in .env file #
###################################################
# get method to be used for spell checking
METHOD = os.environ['CHECK_METHOD']
logging.info('METHOD variable set to {}'.format(METHOD))
assert METHOD in ['norvig', 'edit', 'semantic']
# check if the user wants to run the script run_benchmarks.py to test performance of the implemented methods
RUN_BENCHMARKS = os.environ['RUN_BENCHMARKS'].lower() == 'true'
logging.info('RUN_BENCHMARKS variable set to {}'.format(RUN_BENCHMARKS))

##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'unigram_clean.csv'
if DATA_FILE not in os.listdir(DATA_DIR):
    logging.info('Running data_cleaning.py script to produce vocabulary file {}'.format(DATA_FILE))
    import data_cleaning
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

VOCAB = data.values
VOCAB = {w: c for w, c in VOCAB}

##################################
# Running benchmarks if required #
##################################

if RUN_BENCHMARKS:
    logging.info('Running benchmark script `run_benchmark.py`')
    import run_benchmark

##########################
# Loading FastText model #
##########################
# The fasttext embeddings are loaded only if METHOD is set to 'semantic'

MODEL_DIR = '.'
MODEL_FILE = os.environ['FASTTEXT_MODEL']    # fasttext embeddings


if METHOD == 'semantic':
    download_embeddings(MODEL_DIR, MODEL_FILE)
    assert MODEL_FILE + '.bin' in os.listdir(MODEL_DIR)
    assert MODEL_FILE + '.vec' in os.listdir(MODEL_DIR)
    logging.info('Loading embeddings')
    t0 = time.time()
    EMBEDDING = fText.load_fasttext_format(path.abspath(path.join(MODEL_DIR, MODEL_FILE + '.bin')))
    logging.info('Time to load embeddings: {}'.format(time.time() - t0))


################################
# Spell Checker initialization #
################################

if METHOD == 'norvig':
    # Peter Norvig inspired spell checker
    spell_check = NorvigCheck(VOCAB)
elif METHOD == 'edit':
    # Edit-distance based spell checker
    spell_check = EditDistanceCheck(VOCAB)
elif METHOD == 'semantic':
    # Spell checker based on fasttext word embeddings
    spell_check = SemanticCheck(VOCAB, EMBEDDING)

#################
# API functions #
#################


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def hello_world():
    return Response('App is running. Method used to provide candidates: {}'.format(METHOD), status = 200)

@app.route('/<string:query>', methods = ['GET'])
def get_similar(query: str) -> Response:
    '''
    Returns candidates
    :param query:
    :param words:
    :return:
    '''
    #out = {term: score for term, score in spell_check.spell_check(query)}
    out = {}
    for cand in spell_check.spell_check(query):
        out[cand[0]] = cand[1]
    return Response(json.dumps(out),
                    status = 200,
                    mimetype = 'application/json')

########
# Main #
########


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
