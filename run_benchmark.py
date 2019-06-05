#######################################################################################################
# Script to run timing benchmarks and to generate a comparison of the implemented spell check methods #
#######################################################################################################

#############
# Libraries #
#############

import os
import os.path as path
import time
import pandas as pd
from spellCheck import NorvigCheck, EditDistanceCheck, SemanticCheck
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from gensim.models import FastText as fText
from utilities import download_embeddings

import logging
logger = logging.getLogger('benchmarks')
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('run_benchmark.log')
logger.addHandler(c_handler)
logger.addHandler(f_handler)

############
# Settings #
############

DATA_DIR = 'data/'
MODEL_DIR = '.'
VOCAB_FILE = 'unigram_clean.csv'    # dataset containing medical words (assumed to be spelled correctly)
TEXTS_FILE = 'queries.csv' # dataset of user messages
MODEL_FILE = os.environ['FASTTEXT_MODEL']    # fasttext embeddings

##################
# Importing data #
##################

assert VOCAB_FILE in os.listdir(DATA_DIR)
assert TEXTS_FILE in os.listdir(DATA_DIR)

# load correct spellings from medical corpus
data = pd.read_csv(path.join(DATA_DIR, VOCAB_FILE))
VOCAB = data.values
VOCAB = {w: c for w, c in VOCAB}

# load user messages
messages = pd.read_csv(path.join(DATA_DIR, TEXTS_FILE)).values

######################
# Loading embeddings #
######################

download_embeddings(MODEL_DIR, MODEL_FILE)
assert MODEL_FILE + '.vec' in os.listdir(MODEL_DIR)
assert MODEL_FILE + '.bin' in os.listdir(MODEL_DIR)

logger.info('Loading embeddings')
t0 = time.time()
EMBEDDING = fText.load_fasttext_format(path.join(MODEL_DIR, MODEL_FILE))
logger.info('Time to load embeddings: {}'.format(time.time() - t0))

#################################
# Spell Checker initializations #
#################################

# Peter Norvig inspired spell checker
spell_check_norvig = NorvigCheck(VOCAB)
# Edit-distance based spell checker
spell_check_edit = EditDistanceCheck(VOCAB)
# Spell checker based on fasttext word embeddings
spell_check_semantic = SemanticCheck(VOCAB, EMBEDDING)

##############
##############
# BENCHMARKS #
##############
##############

# Create a matrix with sentences, misspelled words, and the top candidate for each implemented spell check method.
# The sentence is reported to give a context while inspecting the results, in order to measure qualitatively the
# performance of each method. A quantitative measure of the performance should be then assessed using a "truth dataset".
#
# Words that are not present in the vocabulary are taken as misspelled.
# The matrix has the following structure:
# sentence_1 unknown_word_1 candidate_1_1 candidate_1_2 candidate_1_3
# sentence_1 unknown_word_2 candidate_2_1 candidate_2_2 candidate_2_3
# ...
# sentence_n unnkown_word_n candidate_n_1 candidate_n_2 candidate_n_3
#

out = []
for index, message in enumerate(messages):
    message = message[0].lower()
    tokens = word_tokenize(message)
    for token in tokens:
        if (token not in VOCAB) and (token not in ['"','.',"'"]) and (len(token) > 1):
            #print('|{}|'.format(token))
            out.append([message, token])

logger.info('\n#\n# Spell check: {} unknown words found\n#'.format(len(out)))

logger.info('Testing NorvigCheck()')
candidates_norvig = []
t0 = time.time()
for index, el in enumerate(out):
    if index % 100 == 0: logger.info('...analized {} tokens in {} seconds...'.format(index, time.time() - t0))
    guess = spell_check_norvig.spell_check(el[1])
    if not guess:
        guess = ''
    else:
        guess = guess[0][0]
    candidates_norvig.append(guess)
logger.info('...analized {} tokens in {} seconds.\n'.format(index, time.time() - t0))

logger.info('Testing EditDistanceCheck()')
candidates_edit = []
t0 = time.time()
for index, el in enumerate(out):
    if index % 100 == 0: logger.info('...analized {} tokens in {} seconds...'.format(index, time.time() - t0))
    guess = spell_check_edit.spell_check(el[1])
    if not guess:
        guess = ''
    else:
        guess = guess[0][0]
    candidates_edit.append(guess)
logger.info('...analized {} tokens in {} seconds.\n'.format(index, time.time() - t0))

logger.info('Testing SemanticCheck()')
candidates_semantic = []
t0 = time.time()
for index, el in enumerate(out):
    if index % 100 == 0: logger.info('...analized {} tokens in {} seconds...'.format(index, time.time() - t0))
    guess = spell_check_semantic.spell_check(el[1])
    if not guess:
        guess = ''
    else:
        guess = guess[0][0]
    candidates_semantic.append(guess)
logger.info('...analized {} tokens in {} seconds.\n'.format(index, time.time() - t0))


sentences = [el[0] for el in out]
unknown_words = [el[1] for el in out]

results = pd.DataFrame(data = {'sentence': sentences,
                               'unknown_word': unknown_words,
                               'guess_NorvigCheck': candidates_norvig,
                               'guess_EditDistanceCheck': candidates_edit,
                               'guess_SemanticCheck': candidates_semantic})

results.to_csv('data/test_results.csv', index = False)
