import re

from pal.heuristics.heuristic import Heuristic


""" A class to hold response codes.

    The `response` codes are
    0: error - something went wrong or the query could not be answered
    1: success - the query was successfully answered
"""
_response_codes = {
    'ERROR': 0,
    'SUCCESS': 1,
    'NEEDS DATA - USER': 2,
    'NEEDS DATA - CLIENT': 3,
    'EXTERNAL': 4
}

def wrap_response(func):
    """ A wrapper for service response functions
    """
    def fn(*args, **kwargs):
        res = func(*args, **kwargs)
        err_msg = 'Sorry, but I got confused. What did you want?'
        if res is None:
            return {'status': _response_codes['ERROR'], 'summary': err_msg}
        if isinstance(res, dict):
            return res
        if not isinstance(res, (list, tuple)):
            res = (res,)
        if len(res) == 1:
            return {'status': _response_codes['SUCCESS'], 'summary': res[0]}
        elif len(res) == 2:
            key = 'summary'
            if res[0] == 'NEEDS DATA - USER':
                key = 'needs_user'
            elif res[0] == 'NEEDS DATA - CLIENT':
                key = 'needs_client'
            return {'status': _response_codes[res[0]], key: res[1]}
        elif len(res) == 3:
            return {'status': _response_codes[res[0]],
                    'summary': res[1], 'data': res[2]}
        elif len(res) == 5 and res[0] == 'EXTERNAL':
            # implement external services
            # 'action' is thing to do (i.e. post to fb)
            # 'external' is 3rd party service
            return {'status': _response_codes[res[0]], 'payload': 
                    { 'action': res[1], 'data': res[2]},
                    'summary': res[3], 'external': res[4]}
        else:
            return {'status': _response_codes['ERROR'], 'summary': err_msg}
    return fn


class Service(object):

    def __init__(self):
        """ We need the name later for heuristic stuff """
        self.heuristic = Heuristic(self.__class__.short_name())

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

    @classmethod
    def short_name(cls):
        name = cls.__name__
        return re.match('(\w+)Service', name).group(1).lower()
