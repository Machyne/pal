class Service(object):

    def applies_to_me(self, client, feature_request_type):
        """ Returns true if this service is a potentially relevant to the
            specified client and request type.
        """
        raise NotImplementedError()

    def get_confidence(self, features):
        """ Returns a number between 0 and 1 indicating the confidence of
            this service that it is relevant to the specified features.
        """
        raise NotImplementedError()

    def go(self, features):
        """ Returns a response to the specified features, making calls to
            exernal APIs as needed.
        """
        raise NotImplementedError()
