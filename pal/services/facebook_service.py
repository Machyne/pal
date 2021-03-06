#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.
#
# TODO:
# 1. Allow unquoted posting
# (i.e. 'Post Hi from Pal' instad of 'Post "Hi from Pal"')
# 2. Twitter/Other social networks?

import re

from pal.services.base_service import Service
from pal.services.base_service import wrap_response


class FacebookService(Service):
    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        return super(self.__class__, self).get_confidence(params)

    @wrap_response
    def go(self, params):
        query = params['query']

        # if the query has a quoted string,
        # automatically assume the thing between the quotes
        quoted = re.findall(r'"([^"]*)"', query)
        if len(quoted) == 1:
            # found quoted string, just decide the external service
            message = quoted[0]
            # if 'facebook' in features['keywords']:
            # assume facebook for now since there aren't any other services
            return ('EXTERNAL', 'POST', message,
                    "If this got displayed, something's wrong", 'facebook')
