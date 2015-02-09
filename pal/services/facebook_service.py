# TODO:
# 1. Allow unquoted posting
# (i.e. 'Post Hi from Pal' instad of 'Post "Hi from Pal"')
# 2. Twitter/Other social networks?

import re

from pal.services.service import Service
from pal.services.service import wrap_response

class FacebookService(Service):
    def applies_to_me(self, client, feature_request_type):
        return True
    
    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, params):
        features = params['features']
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