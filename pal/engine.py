import logging

from flask import request
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.validator import Validator
from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor
from pal.classifier import Classifier
from pal.executor import Executor
from pal.sanitizer import Sanitizer


class Engine(Resource):
    LOGGER = logging.getLogger('PAL Engine')

    @swagger.operation(
        notes='End-to-end processing from query to response',
        nickname='engine',
        parameters=[
            {
                'name': 'query',
                'description': 'Input query, usually a question or request',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'client',
                'description': 'Identifier for client initiating the request',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        Engine.process(params)
        return params, 200, {'Access-Control-Allow-Origin': '*'}

    @classmethod
    def process(cls, params):
        Validator.process(params)
        if 'error' in params:
            cls.LOGGER.error(message=params['error'])
            abort(404, message=params['error'])
        StandardNLP.process(params)
        FeatureExtractor.process(params)
        Classifier.process(params)
        Executor.process(params)
        # Log the whole process
        cls.LOGGER.info(params)
        Sanitizer.process(params)
