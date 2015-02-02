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
            },
            {
                'name': 'user-data',
                'description': 'Additional data such as location',
                'required': False,
                'allowMultiple': False,
                'dataType': 'json',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        # Convert string-ified user-data to a dict for swagger API.
        data = params.get('user-data', {})
        while not isinstance(data, dict):
            try:
                true, false = True, False
                data = eval(data)
            except Exception:
                data = {}
        params['user-data'] = data
        # Convert [] notation to nested dicts
        bad_nested = [x for x in params if x.startswith('user-data[')]
        if len(bad_nested):
            data = {}
            for key in bad_nested:
                # ignore 'user-data[' and ']'
                data[key[10:-1]] = params[key]
                del params[key]
            params['user-data'] = data
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
