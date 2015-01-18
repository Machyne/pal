# A service for movie info

from api.movie.tmdb_api import get_movie_names_for_person
from pal.services.service import Service
from pal.services.service import wrap_response


class MovieService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, features):
        tagged_nouns = features.get('nouns', [])
        keywords = features.get('keywords', [])
