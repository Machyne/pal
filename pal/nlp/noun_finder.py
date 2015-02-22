from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
from nltk import ne_chunk

from pal.nlp.standard_nlp import StandardNLP


def find_nouns(pos_tokens):
    tree = ne_chunk(pos_tokens)
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
                'name': 'query',
                'description': 'The sentence from which to find nouns.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        StandardNLP.process(params)
        return find_nouns(params['features']['pos'])[1]
