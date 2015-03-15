#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from pal.nlp.standard_nlp import StandardNLP


def is_question(tokens):
    start_words = ['who', 'what', 'when', 'where', 'why', 'how', 'is',
                   'can', 'does', 'do']
    return tokens[0].lower() in start_words or tokens[-1] == '?'


class QuestionDetector(Resource):
    """Swagger resource for QuestionDetector"""
    @swagger.operation(
        notes='Detects Questions',
        nickname='is_question',
        parameters=[
            {
                'name': 'query',
                'description': 'A sentence that might be a question.',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        StandardNLP.process(params)
        return is_question(params['features']['tokens'])
