import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json
from spellCheck import NorvigCheck, EditDistanceCheck, SemanticCheck
from gensim.models import FastText as fText
import logging
logging.basicConfig(#filename='example.log',
                    level=logging.DEBUG)

# TODO: add logging
# TODO: add comment about possibility of having a test file in readme file
# TODO: add sample vocabulary and test files
# TODO: run benchmarks and report output in readme file (see 'Test' section)
# TODO: add automatic download of fasttext embedding if files are not present
# TODO: add list of files in readme

METHOD = os.environ['CHECK_METHOD']
assert METHOD in ['norvig', 'edit', 'semantic']
print('Method selected: {}'.format(METHOD))


##################
# Importing data #
##################

DATA_DIR = 'data/'
DATA_FILE = 'unigram_clean.csv'
if DATA_FILE not in os.listdir(DATA_DIR):
    import data_cleaning
assert DATA_FILE in os.listdir(DATA_DIR)

data = pd.read_csv(path.join(DATA_DIR, DATA_FILE))

VOCAB = data.values
VOCAB = {w: c for w, c in VOCAB}

##########################
# Loading FastText model #
##########################


MODEL_DIR = 'models/'
MODEL_FILE = 'wiki.en'    # fasttext embeddings

if METHOD == 'semantic':
    assert MODEL_FILE + '.bin' in os.listdir(MODEL_DIR)
    assert MODEL_FILE + '.vec' in os.listdir(MODEL_DIR)
    logging.info('Loading embeddings')
    t0 = time.time()
    EMBEDDING = fText.load_fasttext_format(path.abspath(path.join(MODEL_DIR, MODEL_FILE + '.bin')))
    #EMBEDDING = fText.load_fasttext_format('models/' + MODEL_FILE)
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
    # TODO: deactivate debug mode when done
    app.run(debug = True, host = '0.0.0.0')