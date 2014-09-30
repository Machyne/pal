class IMBDService(AbstractService):

    def applies_to_me(self, client, feature_request_type):
        return true

    def get_confidence(self, req, features):
        return 1

    def go(self, features, post_params):
        return {'response': “Tom Hanks was in 1 movies.”}
