#######
# EDA #
#######

# Idea: score the results based on word counts from actual text messages (reported in health_queries), instead of medical
# text (nhs_unigram)

import pandas as pd

UNIGRAMS = '/Users/miche/DataScience/spellCheck/data/nhs_unigram.csv'
MESSAGES = '/Users/miche/DataScience/spellCheck/data/health_queries_clean.csv'

vocab = pd.read_csv(UNIGRAMS)
texts = pd.read_csv(MESSAGES)

# goal: check how many correct medical words are present in the corpus of messages.
# If the number os too low, I use the counts given in the medical corpus.
# If the number is high enough, and the counts are not too low, I can use the counting of the words in the text messages
# as score (or a combination of the two)

print('Number of unique unigrams in medical corpus is {}'.format(vocab.shape[0]))
print('Number of unique unigrams in messages is       {}'.format(texts.shape[0]))

# TODO: print some statistics