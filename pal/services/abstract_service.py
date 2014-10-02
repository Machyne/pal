class AbstractService(object):
    @classmethod
    def magic(cls, more_magic):
        from .imdb_service import IMDBService
        return [IMDBService()]

    def applies_to_me(self, client, feature_request_type):
        """Determines whether this service is a valid possible outcome for the
        given request.
        """
        return

    def get_confidence(self, req, features):
        """Returns a number between 0 and 1 representing the confidence
        of this service that it applies to this request.
        """
        return

    def go(self, features, post_params):
        """Makes any needed calls to external APIs, returns output
        """
        return
