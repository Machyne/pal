from pal.services.service import Service
from pal.services.service import wrap_response
from api.dominos.pizza_options import order_pizza

class DominosService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, params):
        features = params['features']
        tokens = map(str.lower, features['tokens'])
        return 'pizza coming soon'
