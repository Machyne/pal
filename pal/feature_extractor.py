#!/usr/bin/env python
import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger


class FeatureExtractor(Resource):
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
        features = {'keywords': ['movie'],
                    'nouns': nouns,
                    'tense': 'past',
                    'isQuestion': True,
                    'questionType': 'quantity'}
        return features

    @swagger.operation(
        notes='Recognize features',
        nickname='preprocess',
        parameters=[
            {
                'name': 'postags',
                'description': 'Part of Speech Tagged sentence',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        pos = [tuple(x) for x in eval(request.form['postags'])]
        print pos
        return self.extract_features({"pos": pos})
