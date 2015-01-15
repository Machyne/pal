import math
import os

import nltk
from nltk.corpus import qc
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
try:
    import cPickle as pickle
except:
    import pickle

from pal.nlp.standard_nlp import StandardNLP

_QTYPE_DATA = None


def _qtype_tokens(tokens):
    pos = nltk.pos_tag(tokens)
    tokens = map(lambda x: x[1] if 'NN' in x[1] else x[0].lower(), pos)
    tokens = map(lambda x: 'NN' if 'NN' in x and x != 'NNP' else x, tokens)
    return ['^^'] + tokens + ['?']


def _make_qtype_data(verbose=False):
    data = {}
    for fileid in qc.fileids():
        if verbose:
            print fileid
        for type_, sent in qc.tuples(fileid):
            type_ = type_.split(':')[0]
            if type_ not in data:
                data[type_] = {0: 0}
            counts = data[type_]
            tokens = _qtype_tokens(sent.split(' '))
            for i, t in enumerate(tokens):
                counts[0] += 1
                if t not in counts:
                    counts[t] = {0: 0}
                counts[t][0] += 1
                if i + 1 < len(tokens):
                    if tokens[i + 1] not in counts[t]:
                        counts[t][tokens[i + 1]] = {0: 0}
                    counts[t][tokens[i + 1]][0] += 1
                if i + 2 < len(tokens):
                    if tokens[i + 2] not in counts[t][tokens[i + 1]]:
                        counts[t][tokens[i + 1]][tokens[i + 2]] = 0
                    counts[t][tokens[i + 1]][tokens[i + 2]] += 1
    return data


def _load_qtype_data(verbose=False):
    global _QTYPE_DATA
    if _QTYPE_DATA is not None:
        return
    data_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'data', 'qtypes.dat'))
    try:
        with open(data_file, 'rb') as f:
            _QTYPE_DATA = pickle.load(f)
    except Exception:
        _QTYPE_DATA = _make_qtype_data(verbose)
        with open(data_file, 'wb+') as f:
            pickle.dump(_QTYPE_DATA, f)


def _prob(counts, w1, w2=None, w3=None):
    if w3 is None:
        if w2 is None:
            if (w1 not in counts):
                return 0.0
            if counts[w1][0] == 0:
                return 0.0
            else:
                return float(counts[w1][0]) / counts[0]
        else:
            if (w1 not in counts) or (w2 not in counts[w1]):
                return 0.0
            if counts[w1][w2][0] == 0:
                return 0.0
            else:
                return float(counts[w1][w2][0]) / counts[w1][0]
    else:
        if ((w1 not in counts) or (w2 not in counts[w1]) or
                (w3 not in counts[w1][w2])):
            return 0.0
        if counts[w1][w2][w3] == 0:
            return 0.0
        else:
            return float(counts[w1][w2][w3]) / counts[w1][w2][0]


def _prob_star(counts, w1, w2, w3):
    # Magic numbers chosen empirically via testing.
    lmbd3 = 0.3
    lmbd2 = 0.35
    lmbd1 = 0.345
    lmbd0 = 0.005
    # calculations done in log probabilities
    return math.log(lmbd3 * _prob(counts, w1, w2, w3) +
                    lmbd2 * _prob(counts, w1, w2) +
                    lmbd1 * _prob(counts, w1) + lmbd0)


def _get_perplexity(model, tokens):
    prob = 0.0
    token_list = _qtype_tokens(tokens)
    for i, t in enumerate(token_list[:-2]):
        prob += _prob_star(model, t, token_list[i + 1], token_list[i + 2])
    return math.pow(math.e, prob * (-1.0 / len(tokens)))


def classify_question(tokens):
    global _QTYPE_DATA
    _load_qtype_data()
    min_perplex = ('fakename', 9999999999999)
    for type_, model in _QTYPE_DATA.iteritems():
        p = _get_perplexity(model, tokens)
        if p < min_perplex[1]:
            min_perplex = (type_, p)
    if min_perplex[1] > 25.0:
        return 'UNK'
    return str(min_perplex[0])


class QuestionClassifier(Resource):
    """Swagger resource for QuestionClassifier"""
    @swagger.operation(
        notes='Classifies Question Type',
        nickname='qtype',
        parameters=[
            {
                'name': 'question',
                'description': 'The question to classify.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        processed_data = StandardNLP.process(request.form['question'])
        return classify_question(processed_data['tokens'])

if __name__ == '__main__':
    # create and serialize model
    print 'ensuring that the question classification data exists'
    _load_qtype_data(True)
    print 'complete'
