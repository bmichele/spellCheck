import gensim.models.fasttext as fasttext

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


def edit(word):
    #letters = '1234567890£$%&/()=?^qwertyuiopasdfghjklzxcvbnmèé+*òçà°ù§<>,;.:-_'
    letters = 'qwertyuiopasdfghjklzxcvbnm'
    #letters = 'aA' # for testing
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    insert = [ p1 + char + p2 for p1, p2 in splits for char in letters]
    delete = [ p1 + p2[1:] for p1, p2 in splits if len(p2) > 0]
    replace = [ p1 + char + p2[1:] for p1, p2 in splits if len(p2) > 0 for char in letters]
    return list({*insert, *delete, *replace})


def edit2(word):
    out = []
    for edited in edit(word):
        out.extend(edit(edited))
    return list({*out})


def edit3(word):
    out = []
    for edited in edit2(word):
        out.extend(edit(edited))
    return list({*out})


def filter(words: list, vocab: dict) -> list:
    return [(w, vocab.get(w)) for w in words if w in vocab]


def candidates(word: str, vocab: dict) -> list:
    edited = {*edit(word), *edit2(word), word}
    edited = list(edited)
    return sorted(filter(edited, vocab), key = lambda x: x[1], reverse = True)


#####################
# Class definitions #
#####################


class EditDistanceCheck:

    def __init__(self, vocabulary: dict) -> None:
        self._vocabulary = vocabulary

    def spell_check(self, word: str) -> list:
        w0 = list(self._vocabulary.keys())[0]
        d0 = levenshtein(word, w0)
        out = [w0]
        for w in self._vocabulary:
            if d0 == 0:
                break
            if minlevensthein(word, w) > d0:
                continue
            else:
                d = levenshtein(word, w)
                if d < d0:
                    d0 = d
                    out = [w]
                elif d == d0:
                    out.append(w)

        # out = {el: EMBEDDING.wv.similarity(query, el) for el in cand}
        total = sum([self._vocabulary[el] for el in out])
        out = [(el, self._vocabulary[el]/total) for el in out]
        out = sorted(out, key = lambda x: x[1], reverse = True)
        #out = {'edit_distance': d0, 'candidates': out}
        return out


class NorvigCheck:

    def __init__(self, vocabulary: dict) -> None:
        self._vocabolary = vocabulary

    def spell_check(self, word: str) -> list:
        # TODO: improve case in which word is a valid word!!!
        out = candidates(word, self._vocabolary)
        # normalize scores so that sum up to one
        total = sum([c for _, c in out])
        out = [(w, c/total) for w, c in out]
        return out



class SemanticCheck:

    def __init__(self, vocabulary: dict, embeddings: fasttext.FastText) -> None:
        self._vocabulary = vocabulary
        self._model = embeddings

    def spell_check(self, word: str, topn: int = 10) -> list:
        out = [(check, self._model.wv.distance(word, check)) for check in self._vocabulary.keys()]
        out = sorted(out, key = lambda x: x[1])
        out = out[:topn]
        # convert distances to scores
        total = sum([d for _, d in out])
        cands = [w for w, _ in out]
        dists = [d/total for _, d in out]
        dists.reverse()
        out = [(w, d) for w, d in zip(cands, dists)]
        return out
