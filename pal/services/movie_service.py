# A service for movie info

from pal.services.service import Service


class MovieService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    def go(self, features):
        return {'response': 0, 'summary': 'Tom Hanks was in 1 movies.'}
