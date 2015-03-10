import re
from os import path

from pal.services.base_service import Service
from pal.services.base_service import wrap_response


def get_jokes():
    file_path = path.realpath(path.join(path.dirname(__file__),
                                        "jokes.txt"))
    with open(file_path, 'rb') as joke_file:
        for line in joke_file.readlines():
            if line.startswith("#"):
                continue
            prompt, response = map(str.strip, line.split("::", 1))
            yield prompt, response.replace("\\n", "\n")


class JokeService(Service):
    _JOKES = {prompt: response for prompt, response in get_jokes()}

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        for joke in self._JOKES:
            query = re.sub(r'[^a-z ]', '', params['query'].lower())
            if joke in query:
                return 9001
        return 0

    @wrap_response
    def go(self, params):
        for joke in self._JOKES:
            query = re.sub(r'[^a-z ]', '', params['query'].lower())
            if joke in query:
                return self._JOKES[joke]
        return ('ERROR', 'Tom Hanks was in 1 movies.')
