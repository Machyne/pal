from os import path, listdir
import re

from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.nlp.standard_nlp import StandardNLP

_KEYWORDS = None


def _load_keyword_data():
    global _KEYWORDS
    if _KEYWORDS is not None and len(_KEYWORDS):
        return
    _KEYWORDS = set()
    dir_ = path.realpath(
        path.join(
            path.dirname(__file__),
            '..', 'heuristics', 'values'))
    files = [f for f in listdir(dir_) if re.match(r'[a-z]+_values\.txt', f)]
    files = map(lambda f: path.realpath(path.join(dir_, f)), files)
    for file_ in files:
        with open(file_, 'rb') as f:
            for line in f:
                line = line.strip()
                if '[' in line or ']' in line:
                    continue
                word = line.split(',')[0].strip()
                word = re.sub(r'([\*\+\.\]\[\(\)\?])', r'\\\1', word)
                _KEYWORDS.add(word)


def find_keywords(tokens):
    global _KEYWORDS
    _load_keyword_data()
    tokens = ' '.join(tokens).lower()
    return [w for w in _KEYWORDS if re.search(r'(^| )' + w + r'($| )', tokens)]


class KeywordFinder(Resource):
    """Swagger resource for KeywordFinder"""
    @swagger.operation(
        notes='Finds Keywords',
        nickname='keywords',
        parameters=[
            {
                'name': 'query',
                'description': 'The sentence from which to find keywords.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        StandardNLP.process(params)
        return find_keywords(params['features']['tokens'])
