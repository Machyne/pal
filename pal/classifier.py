from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.services import get_service_by_name
from pal.services import get_all_service_names

from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor


class Classifier(Resource):
    @swagger.operation(
        notes=('Get the names of potentially relevant services and pick the '
               'one with the highest confidence.'),
        nickname='classify',
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
        return params

    _CACHE = {}

    @classmethod
    def process(cls, params):
        # Get the names of potentially relevant services
        service_names = get_all_service_names()
        features = params['features']
        client = params['client']
        request_type = (features['questionType'] if 'questionType' in features
                        else features['actionType'])
        key = client, request_type
        if key not in cls._CACHE:
            service_names = filter(
                lambda service: get_service_by_name(service)
                .applies_to_me(*key),
                service_names)
            cls._CACHE[key] = service_names
        else:
            service_names = cls._CACHE[key]
        # Pick the service with the highest confidence
        conf_levels = {service_name: get_service_by_name(service_name)
                       .get_confidence(features)
                       for service_name in service_names}
        params['confidences'] = conf_levels
        params['service'] = (max(conf_levels, key=conf_levels.get) if
                             max(conf_levels.itervalues()) > 0 else None)
