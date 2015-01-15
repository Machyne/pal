#!/usr/bin/env python
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.nlp.keyword_finder import find_keywords
from pal.nlp.noun_finder import find_nouns
from pal.nlp.question_classifier import classify_question
from pal.nlp.question_detector import is_question
from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.tense_classifier import get_tense


class FeatureExtractor(Resource):
    @classmethod
    def process(cls, params):
        """Does semantic analysis stuff, extracts important information
        to NLP'd data.
        """
        tree, nouns = find_nouns(params['pos'])
        keywords = find_keywords(set(x[0] for x in tree if ' ' not in x[0]))
        features = {'keywords': keywords,
                    'nouns': nouns,
                    'tense': get_tense(params['pos']),
                    'isQuestion': is_question(params['tokens']),
                    'questionType': classify_question(
                        params['tokens'])}
        params['features'] = features

    @swagger.operation(
        notes='Recognize features',
        nickname='features',
        parameters=[
            {
                'name': 'query',
                'description': 'Your question or command.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        StandardNLP.process(params)
        FeatureExtractor.process(params)
        return params
