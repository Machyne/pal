#!/usr/bin/env python
import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger


class StandardNLP(Resource):
    @classmethod
    def process(cls, data):
        """Extract syntactic and semantic data using standard NLP."""
        tokens = nltk.word_tokenize(data)
        pos = nltk.pos_tag(tokens)
        processed_data = {'tokens': tokens, 'pos': pos}
        return processed_data

    @swagger.operation(
        notes='Tokenize and Tag Parts of Speach',
        nickname='process',
        parameters=[
            {
                'name': 'sentence',
                'description': 'Your question or command.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        return self.process(request.form['sentence'])
