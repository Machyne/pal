import re

from pal.services.service import Service
from pal.services.service import wrap_response


class JokeService(Service):
    _JOKES = {
        'pod bay doors':
            "I'm sorry Jeff, I'm afraid I can't do that.",
        'laws of robotics':
            "1. A robot may not injure a human being or, through inaction, "
            "allow a human being to come to harm.\n2. A robot must obey the "
            "orders given it by human beings, except where such orders would "
            "conflict with the First Law.\n3. A robot must protect its own "
            "existence as long as such protection does not conflict with the "
            "First or Second Law.",
        'knock knock': "Who's there?",
        'tom hanks': "As far as I'm concerned, Tom Hanks was in 1 movies.",
        "wheres waldo": "He's right there, can't you see him?",
    }

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
