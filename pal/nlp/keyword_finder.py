import math
import os
import re

from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
import nltk
from nltk.corpus import brown
from nltk.corpus import gutenberg
from nltk.corpus import reuters
from nltk.corpus import stopwords
try:
    import cPickle as pickle
except:
    import pickle

from .standard_nlp import StandardNLP

_KEYWORD_DATA = None
_STOPS = stopwords.words('english')


def is_good_word(w):
    global _STOPS
    w = w.lower()
    not_stop = w not in _STOPS
    good = re.match(r'[a-z\'\-.]{2,}|[a-z]', w) is not None
    return not_stop and good


def _make_keyword_data(verbose=False):
    vocab = {}
    corpora = [gutenberg, brown, reuters]
    for corpus in corpora:
        for fileid in corpus.fileids():
            if verbose:
                print fileid
            for sent in corpus.sents(fileid):
                words = [w.lower() for w in sent if is_good_word(w)]
                for w in words:
                    if w in vocab:
                        vocab[w] += 1
                    else:
                        vocab[w] = 1
    return vocab


def _load_keyword_data(verbose=False):
    global _KEYWORD_DATA
    if _KEYWORD_DATA is not None:
        return
    data_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'data', 'counts.dat'))
    try:
        with open(data_file, 'rb') as f:
            _KEYWORD_DATA = pickle.load(f)
    except Exception:
        _KEYWORD_DATA = _make_keyword_data(verbose)
        with open(data_file, 'wb+') as f:
            pickle.dump(_KEYWORD_DATA, f)


def find_keywords(tokens):
    global _KEYWORD_DATA
    THRESHOLD = -5  # TODO : tune this
    tokens = map(lambda x: x.lower(), tokens)
    tokens = filter(is_good_word, tokens)
    _load_keyword_data()
    counts = {x: tokens.count(x) for x in set(tokens)}
    counts = {
        x: math.log(counts[x]) -
        math.log(_KEYWORD_DATA[x] if x in _KEYWORD_DATA else 1)
        for x in counts}
    return [x for x in counts if counts[x] > THRESHOLD]


class KeywordFinder(Resource):
    """docstring for KeywordFinder"""
    @swagger.operation(
        notes='Finds Keywords',
        nickname='keywords',
        parameters=[
            {
                'name': 'sentence',
                'description': 'The sentence from which to find keywords.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        processed_data = StandardNLP.process(request.form['sentence'])
        return find_keywords(processed_data['tokens'])

if __name__ == '__main__':
    # preprocess training data
    print 'ensuring that the count data exists'
    FeatureExtractor._load_keyword_data(True)
    print 'complete'
