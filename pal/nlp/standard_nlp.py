#!/usr/bin/env python
import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger


class StandardNLP(Resource):
    @classmethod
    def process(cls, params):
        """Extract syntactic and semantic data using standard NLP."""
        tokens = map(str, nltk.word_tokenize(params['query']))
        pos = nltk.pos_tag(tokens)
        params['features'] = {'tokens': tokens, 'pos': pos}

    @swagger.operation(
        notes='Tokenize and Tag Parts of Speach',
        nickname='standard_nlp',
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
        return params
