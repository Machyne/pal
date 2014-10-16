class AbstractService(object):
    @classmethod
    def magic(cls, more_magic):
        from .omdb_service import OMDBService
        return [OMDBService()]

    def applies_to_me(self, client, feature_request_type):
        """Determines whether this service is a valid possible outcome for the
        given request.
        """
        return

    def get_confidence(self, features):
        """Returns a number between 0 and 1 representing the confidence
        of this service that it applies to this request.
        """
        return

    def go(self, features):
        """Makes any needed calls to external APIs, returns output
        """
        return
