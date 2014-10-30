#!/usr/bin/env python
import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger


class StandardNLP(Resource):
    @classmethod
    def preprocess(cls, data):
        """parses input into a usable form, applies NLP stuff"""
        tokens = nltk.word_tokenize(data)
        pos = nltk.pos_tag(tokens)
        processed_data = {'tokens': tokens, 'pos': pos}
        return processed_data

    @swagger.operation(
        notes='Toeknize and Tag Parts of Speach',
        nickname='preprocess',
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
        return self.preprocess(request.form['sentence'])
