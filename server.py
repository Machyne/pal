import abc
from flask import Flask
from flask.ext.restful import Api
from flask_restful_swagger import swagger

app = Flask(__name__)

api = swagger.docs(api=Api(app), apiVersion='0.1')

class Server(Object):
    EXPECTED_KEYS = ['query', 'client']

    def validate(self, data):
        for x in EXPECTED_KEYS:
            if x not in data:
                raise MissingKeyException(x)

    def __init__(self):
        self.all_services = AbstractService.magic('more magic')
        self.filter = Filter(self.all_services)

    def main(self):
        # start listening - flask stuff
        pass

    def handleRequest(self, req):
        try:
            validate(req)
        except MissingKeyException as e:
            reply(x) // Or something

        client = req['client']
        processed_data = NLPPreprocessor.preprocess(req)
        features = FeatureExtractor.extractFeatures(processed_data)
        services = self.filter.filter(client, features['request_type'])
        conf_levels = {service: service.get_confidence(req, features)
                       for service in services}
        chosen_service = max(conf_levels, key=conf_levels.get)
        reply(chosen_service.go(features, req))

if __name__ == '__main__':
    Server().main()
