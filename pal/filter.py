class Filter(object):
    def __init__(self, all_services):
        self.cache = {}
        self.all_services = all_services

    def filter(self, client, feature_request_type):
        """Handle the initial filtering of potentially relevant services.
        """
        key = tuple([client, feature_request_type])
        if key not in self.cache:
            ret = filter(
                lambda service: service.applies_to_me(*key),
                self.all_services)
            self.cache[key] = ret
            return ret
        else:
            return self.cache[key]
