class Filter(object):
    def __init__(self, all_services):
        self.cache = {}
        self.all_services = all_services

    def filter(self, client, feature_request_type):
        """Handle the initial filtering of potentially relevant services.
        """
        if (client, feature_request_type) not in self.cache:
            ret = filter(
                lambda service: service.applies_to_me(client,
                                                      feature_request_type),
                self.all_service)
            self.cache[(client, feature_request_type)] = ret
            return ret
        else:
            return self.cache[(client, feature_request_type)]
