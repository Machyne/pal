class Sanitizer():
    _PERMITTED_KEYS = ['result', 'service']

    @classmethod
    def process(cls, params):
        for key in params.keys():
            if key not in cls._PERMITTED_KEYS:
                del params[key]
