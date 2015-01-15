#!/usr/bin/env python
from flask import Blueprint
from flask import Flask
from flask import redirect
from flask import render_template
from flask.ext.restful import Api
from flask_restful_swagger import swagger

from pal.engine import Engine
from pal.validator import Validator
from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor
from pal.classifier import Classifier
from pal.executor import Executor
from pal.nlp.keyword_finder import KeywordFinder
from pal.nlp.noun_finder import NounFinder
from pal.nlp.question_classifier import QuestionClassifier
from pal.nlp.question_detector import QuestionDetector
from pal.nlp.tense_classifier import TenseClassifier


app = Flask(__name__)
app.config['DEBUG'] = True
pal_blueprint = Blueprint('pal_blueprint', __name__)
api_pal = swagger.docs(Api(pal_blueprint), apiVersion='0.1',
                       basePath='http://localhost:5000',
                       resourcePath='/',
                       produces=["application/json", "text/html"],
                       api_spec_url='/spec')
api_pal.add_resource(Engine, '/pal')
api_pal.add_resource(Validator, '/validate')
api_pal.add_resource(StandardNLP, '/standard_nlp')
api_pal.add_resource(FeatureExtractor, '/features')
api_pal.add_resource(Classifier, '/classify')
api_pal.add_resource(Executor, '/execute')
api_pal.add_resource(KeywordFinder, '/features/keywords')
api_pal.add_resource(NounFinder, '/features/nouns')
api_pal.add_resource(QuestionClassifier, '/features/qtype')
api_pal.add_resource(QuestionDetector, '/features/is_question')
api_pal.add_resource(TenseClassifier, '/features/tense')


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
