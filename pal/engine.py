from flask import request
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.exceptions import MissingKeyException
from pal.services.abstract_service import AbstractService
from pal.feature_extractor import FeatureExtractor
from pal.standard_nlp import StandardNLP
from pal.filter import Filter


class Engine(Resource):

    EXPECTED_KEYS = ['query', 'client']

    def validate(self, request):
        for x in Engine.EXPECTED_KEYS:
            if x not in request:
                raise MissingKeyException(x)

    @classmethod
    def end_to_end(cls, query, client):
        # Not sure what this is for
        all_services = AbstractService.magic('more magic')
        filter_ = Filter(all_services)
        # 1. Preprocess
        nlp_data = StandardNLP.process(query)
        # 2. Freature extraction
        features = FeatureExtractor.extract_features(nlp_data)
        # 3. Service classification
        services = filter_.filter(
            client,
            (features['questionType'] if 'questionType' in features
                else features['actionType']))
        conf_levels = {service: service.get_confidence(features)
                       for service in services}
        chosen_service = max(conf_levels, key=conf_levels.get)
        # 4. Service execution
        return chosen_service.go(features)

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
        req_dict = {x: request.form[x] for x in request.form}
        try:
            self.validate(req_dict)
        except MissingKeyException as e:
            abort(404, message=str(e))
        response_dict = Engine.end_to_end(req_dict['query'],
                                          req_dict['client'])
        return response_dict, 200, {'Access-Control-Allow-Origin': '*'}
