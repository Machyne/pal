#!/usr/bin/env python
import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from .question_classifier import classify_question
from .keyword_finder import find_keywords


class FeatureExtractor(Resource):
    PRESENT_TAGS = ['VB', 'VBG', 'VBP', 'VBZ']
    PAST_TAGS = ['VBD', 'VBN']

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
        keywords = find_keywords(set(x[0] for x in tree if ' ' not in x[0]))
        features = {'keywords': keywords,
                    'nouns': nouns,
                    'tense': cls.tense_from_pos(processed_data['pos']),
                    'isQuestion': cls.is_question(processed_data['tokens']),
                    'questionType': classify_question(
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
