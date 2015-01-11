from .abstract_service import AbstractService


class OMDBService(AbstractService):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return 1

    def go(self, features):
        return {'response': "Tom Hanks was in 1 movies."}
