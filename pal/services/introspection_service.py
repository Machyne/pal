import re

from pal.services.service import Service
from pal.services.service import wrap_response


class IntrospectionService(Service):
    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        return 0

    @wrap_response
    def go(self, params):
        return 'I serve butter.'