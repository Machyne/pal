from flask import Flask, redirect, Blueprint, request
from flask.ext.restful import reqparse, abort, Api, Resource, fields, \
    marshal_with
from flask_restful_swagger import swagger

from pal.services.abstract_service import AbstractService
from pal.feature_extractor import FeatureExtractor
from pal.nlp_preprocessor import NLPPreprocessor
from pal.filter import Filter
from pal.exceptions import MissingKeyException

app = Flask(__name__)
pal_blueprint = Blueprint('pal_blueprint', __name__)

###################################
# This is important:
api_pal = swagger.docs(Api(pal_blueprint), apiVersion='0.1',
                    basePath='http://localhost:5000',
                    resourcePath='/',
                    produces=["application/json", "text/html"],
                    api_spec_url='/spec')
###################################

class Server(Resource):

    def validate(self, data):
        EXPECTED_KEYS = ['quest', 'client']
        for x in EXPECTED_KEYS:
            if x not in data:
                raise MissingKeyException(x)

    def __init__(self):
        self.all_services = AbstractService.magic('more magic')
        self.filter = Filter(self.all_services)

    @swagger.operation(
        notes='Get a PAL Response',
        nickname='howdy',
        # Parameters can be automatically extracted from URLs (e.g. <string:id>)
        # but you could also override them here, or add other parameters.
        parameters=[
            {
                'name': 'quest',
                'description': 'Your request to PAL',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'client',
                'description': 'What you be usin',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        # Note: `dict` doesn't work
        req = {x: request.form[x] for x in request.form}

        try:
            self.validate(req)
        except MissingKeyException as e:
            abort(404, message=str(e))

        processed_data = NLPPreprocessor.preprocess(req)
        features = FeatureExtractor.extractFeatures(processed_data)
        services = self.filter.filter(req['client'], features['request_type'])
        conf_levels = {service: service.get_confidence(req, features)
                       for service in services}
        chosen_service = max(conf_levels, key=conf_levels.get)
        return chosen_service.go(features, req), 200, {'Access-Control-Allow-Origin': '*'}


##
## Actually setup the Api resource routing here
##
api_pal.add_resource(Server, '/pal')

@app.route('/docs')
def docs():
    return redirect('/static/docs.html')

@app.route('/')
def index():
    return 'IT WORKS!'

# main doesn't run in wsgi
app.register_blueprint(pal_blueprint, url_prefix='/api')

if __name__ == '__main__':
#    app.register_blueprint(pal_blueprint, url_prefix='/api')
    app.run(debug=True)
