#!/usr/bin/env python
import math
import re
import os

import nltk
from nltk.corpus import brown
from nltk.corpus import gutenberg
from nltk.corpus import qc
from nltk.corpus import reuters
from nltk.corpus import stopwords
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
try:
   import cPickle as pickle
except:
   import pickle


class FeatureExtractor(Resource):
    _stops = stopwords.words('english')
    _keyword_data = None
    _qtype_data = None
    PRESENT_TAGS = ['VB', 'VBG', 'VBP', 'VBZ']
    PAST_TAGS = ['VBD', 'VBN']

    @classmethod
    def is_good_word(cls, w):
        w = w.lower()
        not_stop = w not in cls._stops
        good = re.match(r'[a-z\'\-.]{2,}|[a-z]', w) is not None
        return not_stop and good

    @classmethod
    def _make_keyword_data(cls, verbose=False):
        vocab = {}
        corpora = [gutenberg, brown, reuters]
        for corpus in corpora:
            for fileid in corpus.fileids():
                if verbose:
                    print fileid
                for sent in corpus.sents(fileid):
                    words = [w.lower() for w in sent if cls.is_good_word(w)]
                    for w in words:
                        if w in vocab:
                            vocab[w] += 1
                        else:
                            vocab[w] = 1
        return vocab

    @classmethod
    def _load_keyword_data(cls, verbose=False):
        if cls._keyword_data is not None:
            return
        data_file = os.path.abspath(
            os.path.join(os.path.dirname( __file__ ),
            '..', 'data', 'counts.dat'))
        try:
            with open(data_file, 'rb') as f:
                cls._keyword_data = pickle.load(f)
        except Exception:
            cls._keyword_data = cls._make_keyword_data(verbose)
            with open(data_file, 'wb+') as f:
                pickle.dump(cls._keyword_data, f)

    @classmethod
    def find_keywords(cls, tokens):
        THRESHOLD = -5  # TODO : tune this
        tokens = map(lambda x: x.lower(), tokens)
        tokens = filter(cls.is_good_word, tokens)
        cls._load_keyword_data()
        counts = {x: tokens.count(x) for x in set(tokens)}
        counts = {
            x: math.log(counts[x]) -
               math.log(cls._keyword_data[x] if x in cls._keyword_data else 1)
            for x in counts}
        return [x for x in counts if counts[x] > THRESHOLD]

    @classmethod
    def _qtype_tokens(cls, tokens):
        pos = nltk.pos_tag(tokens)
        tokens = map(lambda x: x[1] if 'NN' in x[1] else x[0].lower(), pos)
        tokens = map(lambda x: 'NN' if 'NN' in x and x != 'NNP' else x, tokens)
        return ['^^'] + tokens + ['?']


    @classmethod
    def _make_qtype_data(cls, verbose=False):
        data = {}
        for fileid in qc.fileids():
            if verbose:
                print fileid
            for type_, sent in qc.tuples(fileid):
                type_ = type_.split(':')[0]
                if type_ not in data:
                    data[type_] = {0: 0}
                counts = data[type_]
                tokens = cls._qtype_tokens(sent.split(' '))
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

    @classmethod
    def _load_qtype_data(cls, verbose=False):
        if cls._qtype_data is not None:
            return
        data_file = os.path.abspath(
            os.path.join(os.path.dirname( __file__ ),
            '..', 'data', 'qtypes.dat'))
        try:
            with open(data_file, 'rb') as f:
                cls._qtype_data = pickle.load(f)
        except Exception:
            cls._qtype_data = cls._make_qtype_data(verbose)
            with open(data_file, 'wb+') as f:
                pickle.dump(cls._qtype_data, f)

    @classmethod
    def _prob(cls, counts, w1, w2=None, w3=None):
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

    @classmethod
    def _prob_star(cls, counts, w1, w2, w3):
        # Magic numbers chosen empirically via testing.
        lmbd3 = 0.3
        lmbd2 = 0.35
        lmbd1 = 0.345
        lmbd0 = 0.005
        # calculations done in log probabilities
        return math.log(lmbd3 * cls._prob(counts, w1, w2, w3) +
                        lmbd2 * cls._prob(counts, w1, w2) +
                        lmbd1 * cls._prob(counts, w1) + lmbd0)

    @classmethod
    def _get_perplexity(cls, model, tokens):
        prob = 0.0
        token_list = cls._qtype_tokens(tokens)
        for i, t in enumerate(token_list[:-2]):
            prob += cls._prob_star(model, t, token_list[i + 1], token_list[i + 2])
        return math.pow(math.e, prob * (-1.0 / len(tokens)))

    @classmethod
    def classify_question(cls, tokens):
        cls._load_qtype_data()
        min_perplex = ('fakename', 9999999999999)
        for type_, model in cls._qtype_data.iteritems():
            p = cls._get_perplexity(model, tokens)
            if p < min_perplex[1]:
                min_perplex = (type_, p)
        if min_perplex[1] > 25.0:
            return 'UNK'
        return str(min_perplex[0])

    @classmethod
    def tense_from_pos(cls, pos):
        present_count = len([True for x in pos if x[1] in cls.PRESENT_TAGS])
        past_count = len([True for x in pos if x[1] in cls.PAST_TAGS])
        return 'past' if past_count >= present_count else 'present'

    @classmethod
    def is_question(cls, tokens):
        start_words = ['who', 'what', 'when', 'where', 'why', 'how', 'is',
                       'can', 'does', 'do']
        return tokens[0].lower() in start_words or tokens[-1] == '?'

    @classmethod
    def extract_features(cls, processed_data):
        """Does semantic analysis stuff, extracts important information
        to NLP'd data.
        """
        tree = nltk.ne_chunk(processed_data['pos'])
        tree = [(token if isinstance(token, tuple) else
                 (' '.join(map(lambda a: a[0], token.leaves())),
                  token.label()))
                for token in tree]
        nouns = [token for token in tree
                 if 'NN' in token[1] or ' ' in token[0]]
        keywords = cls.find_keywords(set(x[0] for x in tree if ' ' not in x[0]))
        features = {'keywords': keywords,
                    'nouns': nouns,
                    'tense': cls.tense_from_pos(processed_data['pos']),
                    'isQuestion': cls.is_question(processed_data['tokens']),
                    'questionType': cls.classify_question(
                        processed_data['tokens'])}
        return features

    @swagger.operation(
        notes='Recognize features',
        nickname='features',
        parameters=[
            {
                'name': 'postags',
                'description': 'Part of Speech Tagged sentence',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'tokens',
                'description': 'Tokenized sentence',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        pos = map(tuple, eval(request.form['postags']))
        tokens = eval(request.form['tokens'])
        return self.extract_features({"pos": pos, "tokens": tokens})

if __name__ == '__main__':
    # preprocess training data
    print 'ensuring that the count data exists'
    FeatureExtractor._load_keyword_data(True)
    FeatureExtractor._load_qtype_data(True)
    print 'complete'
