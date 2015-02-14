# From the Wolfram Site
# APP NAME: PAL
# APPID: QG6645-R77PAAXQX9

APPID = "QG6645-R77PAAXQX9"

import urllib
import xml.etree.ElementTree as ET

import requests

from pal.services.service import Service
from pal.services.service import wrap_response

class WAService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        my_confidence = super(self.__class__, self).get_confidence(features)
        fall_back = 15
        return max(my_confidence, fall_back)

    @wrap_response
    def go(self, params):
        query = params['query']
        # Construct a url string based off of the features
        query_url = ("http://api.wolframalpha.com/v2/query?input={}&"
                     "appid={}&podindex=2")
        # Rebuild original query from features dictionary
        input_url = urllib.quote(query, '')
        query_url = query_url.format(input_url, APPID)

        # send the query to WA
        response = requests.get(query_url)

        # parse the WA results
        root = ET.fromstring(response.text)
        return_value = "Error: No Valid Response from Wolfram Alpha"

        # return parsed output
        if root[0][0].tag == 'subpod':
            for element in root[0][0]:
                if element.tag == 'plaintext':
                    return_value = element.text
                    return {'SUCCESS', return_value, return_value}

        return {'ERROR', return_value}

if __name__ == '__main__':
    my_WA_service = WAService()
    params = {"query":"What is the distance from the earth to the moon"}
    print my_WA_service.go(params)
