from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.nlp.standard_nlp import StandardNLP

PRESENT_TAGS = ['VB', 'VBG', 'VBP', 'VBZ']
PAST_TAGS = ['VBD', 'VBN']


def get_tense(pos):
    present_count = len([True for x in pos if x[1] in PRESENT_TAGS])
    past_count = len([True for x in pos if x[1] in PAST_TAGS])
    return 'past' if past_count > present_count else 'present'


class TenseClassifier(Resource):
    """Swagger resource for TenseClassifier"""
    @swagger.operation(
        notes='Classifies Tenses',
        nickname='tense',
        parameters=[
            {
                'name': 'query',
                'description': 'The sentence to classify.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        StandardNLP.process(params)
        return get_tense(params['features']['pos'])
