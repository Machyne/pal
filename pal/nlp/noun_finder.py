import nltk
from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from .standard_nlp import StandardNLP


def find_nouns(pos_tokens):
    tree = nltk.ne_chunk(pos_tokens)
    tree = [(token if isinstance(token, tuple) else
             (' '.join(map(lambda a: a[0], token.leaves())),
              token.label()))
            for token in tree]
    nouns = [token for token in tree
             if 'NN' in token[1] or ' ' in token[0]]
    return tree, nouns


class NounFinder(Resource):
    """Swagger resource for NounFinder"""
    @swagger.operation(
        notes='Finds Nouns',
        nickname='nouns',
        parameters=[
            {
                'name': 'sentence',
                'description': 'The sentence from which to find nouns.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        processed_data = StandardNLP.process(request.form['sentence'])
        return find_nouns(processed_data['pos'])[1]
