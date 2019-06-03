## Installation
Prerequisites: `docker`, `docker-compose`

Clone the repository,
```
git clone https://github.com/bmichele/spellCheck.git
```
then run
```
cd spellCheck
make build
```
to build the docker container.

## Run the service

The spell checker needs, as input, a vocabulary containing correct words with probabilities.
Typically, the file can be obtained processing a large corpus of correctly spelled texts.
The probability for each word can be estimated using the respective count.

The vocabulary must be placed in the data folder and named `nhs_unigram.txt`.
An sample vocabulary containing a limited number of words can be found comes with the repo.
You should replace it with your own vocabulary file before running the service.

## Usage

The spell check comes with three different methods to suggest candidates and compute scores.
The method must be specified in the `.env` file before running the service, and can be
* `norvig`
* `edit`
* `semantic`

Below, the three methods are briefly explained.

### Implemented Methods

#### Norvig's method

Setting `METHOD=norvig` in the `.env` file, the spell-check algorithm used is similar to the algorithm explained by
Peter Norvig in his [post](https://norvig.com/spell-correct.html).
Essentially, the spell checker returns candidates with edit distance up to 2 from the query term taken from the given
vocabulary. The candidates are sorted by the counts specified in the vocabulary (higher count implies higher score). 

#### Edit distance

Setting `METHOD=edit` in the `.env` file, the spell-check algorithm returns, among the vocabulary's words, those that
have the lower edit distance. Each candidate comes with a score computed from the word counts reported in the vocabulary
(higher count implies higher score). The implementation given in this repository is quite efficient (it computes the
[Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) of the query term with almost every word in
the given vocabulary) and should be improved, e.g. using a trie (see this [blog post](http://stevehanov.ca/blog/index.php?id=114)
for an example).

#### Semantic distance

Setting `METHOD=semantic` in the `.env` file, given a misspelled word. the algorithm provides the first 10 closest words
 of the vocabulary.
The distance is computed as the euclidean distance from the misspelled word to the vocabulary's words. The algorithm
uses the [FastText](https://fasttext.cc) embeddings, which provide vectors for out-of-vocabulary words.

_DISCLAIMER_ This implementation is quite slow and eats a lot of memory, and has been implemented with the only purpose
of testing a similarity-based approach to the spell-check problem.

### Running the app

Start the docker container running
```
make start
```
in the main repo folder.

Go to `http://localhost:5000` to check if the application is running.
To get candidatess for a misspelled word, enter the url `http://localhost:5000/tesr`.
You should get a json with candidates and their respective scores.
```
{  
   "test":0.9076850984067479,
   "tear":0.08153701968134958,
   "esr":0.010309278350515464,
   "tes":0.00046860356138706655
}
```

### Stopping the app

Stop the docker container running
```
make stop
```
in the main repo folder.

## Tests

## Conclusions and future work

## Files

* `spellCheck.py` file containing three different spell checker implementations
* `app.py` implementation of Flask service
* `EDA.py` script to get some stats about the datasets
* `data_cleaning.py` script to process files stored in folder `./data`
* `run_benchmark.py` file to test the three spellCheck implementations
* `Dockerfile` docker file
* `docker-compose.py` docker compose file
* `requirements.txt` requirements
