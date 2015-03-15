#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from flask import request
from flask.ext.restful import Resource
from flask_restful_swagger import swagger


class Validator(Resource):
    REQUIRED_KEYS = ['query', 'client']

    @classmethod
    def process(cls, params):
        """ Adds an error to the params if they are invalid.
        """
        missing_keys = []
        for x in Validator.REQUIRED_KEYS:
            if x not in params:
                missing_keys.append(x)
        if missing_keys:
            error_message = ('[Validator] Missing keys: %s'
                             .format(', '.join(missing_keys)))
            params['error'] = error_message

    @swagger.operation(
        notes='Validate',
        nickname='validate',
        parameters=[
            {
                'name': 'query',
                'description': ('Returns true if the request '
                                'contains all required keys.'),
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'client',
                'description': 'Identifier for client initiating the request',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ])
    def post(self):
        params = {x: request.form[x] for x in request.form}
        Validator.process(params)
        return params
