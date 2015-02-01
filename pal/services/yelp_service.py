from api.yelp import yelp_api
from pal.services.service import Service
from pal.services.service import wrap_response


class YelpService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, params):
        print 'here', params.get('user-data', {})
        if 'location' not in params.get('user-data', {}):
            return ('NEEDS MORE',
                {'location':
                    {'type': 'loc',
                     'default': [44.46126762422732, -93.15553424445801]}})
        try:
            lat, lon = map(float, params['user-data']['location'].split(','))
        except Exception:
            return ('ERROR', "I can't handle that format of location data.")
        return 'OMG I HAZ A YELP AT {}, {}!'.format(lat, lon)
