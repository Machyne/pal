class AbstractService(object):

    def applies_to_me(client, feature_request_type):
        """Determines whether this service is a valid possible outcome for the
        given request.
        """
        return

    def get_confidence(req, features):
        """Returns a number between 0 and 1 representing the confidence
        of this service that it applies to this request.
        """
        return

    def go(features, post_params):
        """Makes any needed calls to external APIs, returns output
        """
        return
