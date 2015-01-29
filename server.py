#!/usr/bin/env python
import logging
from logging import Formatter

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


@app.route('/debug')
def debug():
    return render_template('debug.html')

# main doesn't run in wsgi
app.register_blueprint(pal_blueprint, url_prefix='/api')

# configure logging for pal engine
logger = logging.getLogger('PAL Engine')
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    file_handler = logging.FileHandler('flask_pal.log')
else:
    # if being run on the server, use different file
    file_handler = logging.FileHandler('/var/www/pal/flask_pal.log')
file_handler.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# formatter only supports %s formatting
formatter = Formatter('%(asctime)s - %(name)s %(levelname)s:\n'
                      '    [in %(pathname)s:%(lineno)d]\n'
                      '    %(message)s\n'
                      '----')
ch.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(file_handler)


if __name__ == '__main__':
    # app.register_blueprint(pal_blueprint, url_prefix='/api')
    app.run(debug=True)
