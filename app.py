import time
import os
import os.path as path
import pandas as pd
from flask import Flask, Response
import json
from spellCheck import NorvigCheck, EditDistanceCheck, SemanticCheck
from gensim.models import FastText as fText
import data_cleaning
# TODO: add logging

# TODO: replace with argument parsed from command line
# parser = argparse.ArgumentParser(prog = 'Spell Check',
#                                  description = '''
#                                  Launch a spell check app on localhost:5000.
#                                  A method argument must be choosen among `norvig`, `edit` or `semantic`.
#                                   ''')
# parser.add_argument('method', default='norvig', type = str)
# args = parser.parse_args()
# METHOD = args.method
METHOD = os.environ['CHECK_METHOD']
assert METHOD in ['norvig', 'edit', 'semantic']
print('Method selected: {}'.format(METHOD))


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


MODEL_DIR = 'models/'
MODEL_FILE = 'wiki.en'    # fasttext embeddings

if METHOD == 'semantic':
    assert MODEL_FILE + '.bin' in os.listdir(MODEL_DIR)
    assert MODEL_FILE + '.vec' in os.listdir(MODEL_DIR)
    print('Loading embeddings')
    t0 = time.time()
    EMBEDDING = fText.load_fasttext_format(path.join(MODEL_DIR, MODEL_FILE))
    print('Time to load embeddings: {}'.format(time.time() - t0))


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