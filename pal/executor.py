from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.services import get_service_by_name

from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor
from pal.classifier import Classifier


class Executor(Resource):
    @swagger.operation(
        notes='Executor',
        nickname='executor',
        parameters=[
            {
                'name': 'query',
                'description': '',
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
        StandardNLP.process(params)
        FeatureExtractor.process(params)
        Classifier.process(params)
        Executor.process(params)
        return params

    NO_RESPONSE = {
        'response_code': 1,
        'response': "Sorry, I'm not sure what you mean."
    }

    @classmethod
    def process(cls, params):
        service = get_service_by_name(params['service'])
        if service:
            params['result'] = service.go(params['features']) \
                or cls.NO_RESPONSE
        else:
            params['error'] = '[Executor] Invalid service'
            params['result'] = cls.NO_RESPONSE