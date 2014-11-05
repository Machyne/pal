#!/usr/bin/env python
import math
import re

import nltk
from nltk.corpus import brown
from nltk.corpus import gutenberg
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
    _count_data = None
    PRESENT_TAGS = ['VB', 'VBG', 'VBP', 'VBZ']
    PAST_TAGS = ['VBD', 'VBN']

    @classmethod
    def is_good_word(cls, w):
        w = w.lower()
        not_stop = w not in cls._stops
        good = re.match(r'[a-z\'\-.]{2,}|[a-z]', w) is not None
        return not_stop and good

    @classmethod
    def _make_count_data(cls, verbose=False):
        vocab = {}
        corpora = [gutenberg, brown, reuters]
        for corpus in corpora:
            for fileid in corpus.fileids():
                if verbose:
                    print corpus, fileid
                for sent in corpus.sents(fileid):
                    words = [w.lower() for w in sent if cls.is_good_word(w)]
                    for w in words:
                        if w in vocab:
                            vocab[w] += 1
                        else:
                            vocab[w] = 1
        return vocab

    @classmethod
    def _load_count_data(cls):
        if cls._count_data is not None:
            return
        try:
            with open('data/counts.dat', 'rb') as f:
                cls._count_data = pickle.load(f)
        except Exception:
            cls._count_data = cls._make_count_data()
            with open('data/counts.dat', 'wb+') as f:
                pickle.dump(cls._count_data, f)

    @classmethod
    def find_keywords(cls, tokens):
        THRESHOLD = -5  # TODO : tune this
        tokens = map(lambda x: x.lower(), tokens)
        tokens = filter(cls.is_good_word, tokens)
        cls._load_count_data()
        counts = {x: tokens.count(x) for x in set(tokens)}
        counts = {
            x: math.log(counts[x]) -
               math.log(cls._count_data[x] if x in cls._count_data else 1)
            for x in counts}
        return [x for x in counts if counts[x] > THRESHOLD]

    @classmethod
    def tense_from_pos(cls, pos):
        present_count = len([True for x in pos if x[1] in cls.PRESENT_TAGS])
        past_count = len([True for x in pos if x[1] in cls.PAST_TAGS])
        print present_count, past_count
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
        keywords = cls.find_keywords(processed_data['tokens'])
        features = {'keywords': keywords,
                    'nouns': nouns,
                    'tense': cls.tense_from_pos(processed_data['pos']),
                    'isQuestion': cls.is_question(processed_data['tokens']),
                    'questionType': 'quantity'}
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
    FeatureExtractor._load_count_data(True)
    print 'complete'
