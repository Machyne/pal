#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.import urllib

import xml.etree.ElementTree as ET

import requests

from pal.services.base_service import Service
from pal.services.base_service import wrap_response

from config import WA_KEY


class WAService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        my_confidence = (super(self.__class__, self)
                         .get_confidence(params))
        fall_back = 9
        return max(my_confidence, fall_back)

    @wrap_response
    def go(self, params):
        query = params['query']
        # Construct a url string based off of the features
        query_url = ("http://api.wolframalpha.com/v2/query?input={}&"
                     "appid={}&podindex=2")
        # Rebuild original query from features dictionary
        input_url = urllib.quote(query, '')
        query_url = query_url.format(input_url, WA_KEY)

        # send the query to WA
        response = requests.get(query_url)

        # parse the WA results
        root = ET.fromstring(response.text)
        return_value = "I'm sorry, I couldn't find what you were looking for."

        # return parsed output
        if root[0][0].tag == 'subpod':
            for element in root[0][0]:
                if element.tag == 'plaintext':
                    return_value = element.text
                    return ('SUCCESS', return_value)

        return ('ERROR', return_value)


if __name__ == '__main__':
    my_WA_service = WAService()
    params = {'query': "What is the distance from the earth to the moon"}
    print my_WA_service.go(params)
