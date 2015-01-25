from pal.heuristics.heuristic import Heuristic


class Service(object):
    name = 'abstract_service'

    def __init__(self):
        """ We need the name later for heuristic stuff """
        self.heuristic = Heuristic(self.name)

    def applies_to_me(self, client, feature_request_type):
        """ Returns true if this service is a potentially relevant to the
            specified client and request type.
        """
        raise NotImplementedError()

    def get_confidence(self, features):
        """ Returns a number between -Inf and +Inf indicating the confidence of
            this service that it is relevant to the specified features.
        """
        return self.heuristic.run_heuristic(features['keywords'])

    def go(self, features):
        """ Returns a response to the specified features, making calls to
            exernal APIs as needed.
        """
        raise NotImplementedError()
