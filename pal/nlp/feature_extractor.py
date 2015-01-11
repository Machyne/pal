#!/usr/bin/env python
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from .keyword_finder import find_keywords
from .noun_finder import find_nouns
from .question_classifier import classify_question
from .question_detector import is_question
from .tense_classifier import get_tense


class FeatureExtractor(Resource):
    @classmethod
    def extract_features(cls, processed_data):
        """Does semantic analysis stuff, extracts important information
        to NLP'd data.
        """
        tree, nouns = find_nouns(processed_data['pos'])
        keywords = find_keywords(set(x[0] for x in tree if ' ' not in x[0]))
        features = {'keywords': keywords,
                    'nouns': nouns,
                    'tense': get_tense(processed_data['pos']),
                    'isQuestion': is_question(processed_data['tokens']),
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
