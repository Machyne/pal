from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from .standard_nlp import StandardNLP


def is_question(tokens):
    start_words = ['who', 'what', 'when', 'where', 'why', 'how', 'is',
                   'can', 'does', 'do']
    return tokens[0].lower() in start_words or tokens[-1] == '?'


class QuestionDetector(Resource):
    """docstring for QuestionDetector"""
    @swagger.operation(
        notes='Detects Questions',
        nickname='is_question',
        parameters=[
            {
                'name': 'sentence',
                'description': 'A sentence that might be a question.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        processed_data = StandardNLP.process(request.form['sentence'])
        return is_question(processed_data['tokens'])
