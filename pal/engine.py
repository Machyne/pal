from flask import request
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from .exceptions import MissingKeyException
from .filter import Filter
from nlp.feature_extractor import FeatureExtractor
from nlp.standard_nlp import StandardNLP
from services import ALL_SERVICES


class Engine(Resource):

    REQUIRED_KEYS = ['query', 'client']
    NO_RESPONSE = {
        'response_code': 1,
        'response': "Sorry, I'm not sure what you mean."
    }

    @classmethod
    def validate(cls, request):
        """ Raises an exception if a request doesnt contain all required keys.
        """
        for x in cls.REQUIRED_KEYS:
            if x not in request:
                raise MissingKeyException(x)

    @classmethod
    def end_to_end(cls, query, client):
        """ Processes a query "from end to end" doing all steps including
            NLP, feature extraction, service selection, and service execution.
        """
        # 1. Preprocess
        nlp_data = StandardNLP.process(query)
        # 2. Feature extraction
        features = FeatureExtractor.extract_features(nlp_data)
        # 3. Service classification
        filter_ = Filter(ALL_SERVICES)
        services = filter_.filter(
            client,
            (features['questionType'] if 'questionType' in features
                else features['actionType']))
        conf_levels = {service: service.get_confidence(features)
                       for service in services}
        chosen_service = max(conf_levels, key=conf_levels.get)
        # 4. Service execution
        response = chosen_service.go(features)
        return response if response else cls.NO_RESPONSE

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
