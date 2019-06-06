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

The vocabulary must be placed in the data folder and named `unigram.txt`.
A sample vocabulary containing a limited number of words can be found in the folder `data`.
You should replace it with your own vocabulary file before running the service.

## Usage

### Settings

The spell check comes with three different methods to suggest candidates and compute scores.
The method must be specified in the `.env` file before running the service, and can be
* `norvig`
* `edit`
* `semantic`

When `METHOD=semantic` in the `.env` file, it is possible to choose the [fasttext](https://fasttext.cc) word vectors among the
models listed [here](https://fasttext.cc/docs/en/pretrained-vectors.html).

To test how the different methods perform and compare the results, it is possible to specify `BENCHMARKS=true` in the `.env` file.
Note that, in order to run the benchmarks, a file `queries.csv` containing sentences with misspelled words must be provided in the `data` folder.

### Implemented Methods

Here, we briefly explain the implemented methods.

#### Norvig's method

Setting `METHOD=norvig` in the `.env` file, the spell-check algorithm used is similar to the algorithm explained by
Peter Norvig in his [blog post](https://norvig.com/spell-correct.html).
Essentially, the spell checker returns candidates with edit distance up to 2 from the query term taken from the given
vocabulary. The candidates are sorted by the counts specified in the vocabulary (higher count implies higher score). 

#### Edit distance

Setting `METHOD=edit` in the `.env` file, the spell-check algorithm returns, among the vocabulary's words, those that
have the lower edit distance. Each candidate comes with a score computed from the word counts reported in the vocabulary
(higher count implies higher score). The implementation given in this repository is quite inefficient (it computes the
[Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) of the query term with almost every word in
the given vocabulary) and should be improved, e.g. using a trie (see this [blog post](http://stevehanov.ca/blog/index.php?id=114)
for an example). For this reason, the implemented `levenshtein` function has been replaced by the edit distance function
provided by the [editdistance](https://github.com/aflc/editdistance) package.

#### Semantic distance

Setting `METHOD=semantic` in the `.env` file, given a misspelled word, the algorithm provides the first 10 closest words
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
in the main repo folder. Another option, which allows to inspect what the app is doing, is to run
```
docker-compose up
```

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

_DISCLAIMER_ The result strongly depends on the vocabulary file, so you will not get this result using the sample files provided here.

### Stopping the app

Stop the docker container running
```
make stop
```
in the main repo folder.

## Results

The methods have been tested against a corpus of about 27000 sentences containing typos, using a vocabulary of 23000
unique tokens.
The sentences contained, counting duplicates, 5935 unknown words. The `run_benchmarks.py` script produced the following output:

```text
Loading embeddings
Time to load embeddings: 46.77863526344299

#
# Spell check: 5935 unknown words found
#
Testing NorvigCheck()
[...]
...analized 5935 tokens in 330.8887412548065 seconds.

Testing EditDistanceCheck()
[...]
...analized 5935 tokens in 100.25745248794556 seconds.

Testing SemanticCheck()
[...]
...analized 5935 tokens in 10342.194310426712 seconds.
```

The best performance (in terms of CPU time) is achieved returning, for each unknown word, the words with the lower edit
distance that are present in the vocabulary (`EditDistanceCheck()` method). The fact that this naive implementation is the fastest is due to the fact
that the levenshtein distance is computed with C++ and Cython.

The performance of the Norvig's method `NorvigCheck()` is very good, but the method is not able to provide a candidate if there is no
vocabulary word with an edit distance <= 2 with respect to the misspelled word.

The method `SemanticCheck()`, based on semantic similarity between the misspelled word and the vocabulary words is the slowest.
It has been implemented with the only purpose of checking how the FastText word vectors can be used to find distances
between known words and out-of-vocabulary words. Indeed, the model is able to provide word vectors even for misspelled
words.

Analyzing sentences with misspelled words, it is possible to see how `EditDistanceCheck()` and `NorvigCheck()` usually return
consistent results. `SemanticCheck()` returns funky results, but it might be used in combination with the other methods.
For instance, it could be used in the computation of the candidates' scores (e.g. considering the context in which the
misspelled word is used and providing the candidate with the highest semantic similarity).

## Files

* `app.py` run Flask service.
* `spellCheck.py` file containing three different spell checker implementations.
* `utilities.py` contains definitions of some helper functions.
* `data/unigram.txt` sample file to be replaced with your own vocabulary file (should be formatted in the same way).
* `data/queries.csv` sample file to be replaced with your own file (should be formatted in the same way).
* `data_cleaning.py` script to process files stored in folder `data` before running the app.
* `.env` configuration file to set method, semantic model, and specify if benchmarks should be run when app is launched.
* `run_benchmark.py` file to test the different spell check implementations (run if $RUN_BENCHMARKS is set to `true` in `.env` file).

Docker-related:
* `Dockerfile` docker file for service.
* `docker-compose.py` docker compose file for service.
* `requirements.txt` python packages installed in docker container.

### Output files

Running the app, some files are produced.

Files produced by `data_cleaning.py`:
* `data/unigram_clean.csv` vocabulary file formatted in csv obtained from `unigram.txt`. Each line correspond to a word. Columns are 'word' and 'count'.
* `data/queries_clean.csv` contains the words that are present in the file `queries.csv`. Each word is reported with the corresponding count.

Other files:
* `run_benchmarks.log` log file containing benchmarks results.
* `data/test_results.csv` comparison of results obtained using the implemented spell-check methods. Each line reports:
context of the misspelled word, misspelled word, best candidate from NorvigCheck, EditDistanceCheck, SemanticCheck.
The file is produced running `run_benchmarks.py`.
* fasttext model files downloaded to use SemanticCheck.

## Acknowledgments

* [Flask](http://flask.pocoo.org)
* [gensim](https://radimrehurek.com/gensim/)
* [editdistance](https://github.com/aflc/editdistance)
* [nltk](https://www.nltk.org)
* [pandas](https://pandas.pydata.org)