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
        ud = params.get('user-data', {})
        required = [
            ('name', {
                'type': 'str',
                'name': 'name',
            }),
            ('phone', {
                'type': 'str',
                'name': 'phone number',
            }),
            ('address', {
                'type': 'str',
                'name': 'address',
            }),
            ('cc-number', {
                'type': 'hidden',
                'name': 'credit card number',
            }),
            ('cc-type', {
                'type': 'hidden',
                'name': 'credit card type',
            }),
            ('cc-expiration', {
                'type': 'hidden',
                'name': 'credit card expiration date',
            }),
            ('cvv', {
                'type': 'hidden',
                'name': 'cvv',
            }),
            ('cc-zip', {
                'type': 'hidden',
                'name': 'credit card zip code',
            }),
        ]
        needs = []
        for req in required:
            if req[0] not in ud:
                needs.append(req)
        if len(needs):
            return ('NEEDS DATA - USER', needs)
        features = params['features']
        tokens = map(str.lower, features['tokens'])
        return 'pizza coming soon'
