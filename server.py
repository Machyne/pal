#!/usr/bin/env python
from flask import Flask
from flask import redirect
from flask import Blueprint
from flask import request
from flask import render_template
from flask.ext.restful import abort
from flask.ext.restful import Api
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.exceptions import MissingKeyException
from pal.filter import Filter
from pal.nlp.feature_extractor import FeatureExtractor
from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.keyword_finder import KeywordFinder
from pal.nlp.noun_finder import NounFinder
from pal.nlp.question_classifier import QuestionClassifier
from pal.nlp.question_detector import QuestionDetector
from pal.nlp.tense_classifier import TenseClassifier
from pal.services.abstract_service import AbstractService

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
        # Parameters can be automatically extracted from URLs
        # (e.g. <string:id>) but you could also override them here,
        # or add other parameters.
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

        nlp_data = StandardNLP.process(req['quest'])
        features = FeatureExtractor.extract_features(nlp_data)
        services = self.filter.filter(
            req['client'],
            (features['questionType'] if 'questionType' in features
                else features['actionType']))
        conf_levels = {service: service.get_confidence(features)
                       for service in services}
        chosen_service = max(conf_levels, key=conf_levels.get)
        return chosen_service.go(features), 200,
        {'Access-Control-Allow-Origin': '*'}


##
# Actually setup the api resource routing here
##
api_pal.add_resource(Server, '/pal')
api_pal.add_resource(StandardNLP, '/preprocess')
api_pal.add_resource(FeatureExtractor, '/features')
api_pal.add_resource(KeywordFinder, '/keywords')
api_pal.add_resource(NounFinder, '/nouns')
api_pal.add_resource(QuestionClassifier, '/qtype')
api_pal.add_resource(QuestionDetector, '/is_question')
api_pal.add_resource(TenseClassifier, '/tense')


@app.route('/docs')
def docs():
    return redirect('/static/docs.html')


@app.route('/')
def index():
    return render_template('home.html')

# main doesn't run in wsgi
app.register_blueprint(pal_blueprint, url_prefix='/api')

if __name__ == '__main__':
    # app.register_blueprint(pal_blueprint, url_prefix='/api')
    app.run(debug=True)
