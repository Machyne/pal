# A service for movie info

from api.movie.tmdb_api import get_credits_by_name
from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parse
from pal.services.service import Service
from pal.services.service import wrap_response


class MovieService(Service):

    def __init__(self):
        self.grammar = get_grammar_for_service(self.__class__.short_name())
        self.kb = {}

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        # TODO: Actually get params rather than features.
        query = params['query']
        return 100 if parse(query, self.grammar) else 0
        # return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, params):
        query = params['query']
        parse_tree = parse(query, self.grammar)
        if parse_tree:
            intent = self.extract_intent(parse_tree)
            object_ = self.extract_object(parse_tree)
            self.update_kb(intent, object_)
            result = self.query_kb(intent, object_)
            summary = self.generate_summary(intent, object_, result)
            return ('SUCCESS', summary)
        else:
            return ('ERROR', 'I don\'t understand.')

    @staticmethod
    def extract_intent(parse_tree):
        return ('CREDITS', 'COUNT_OF')

    @staticmethod
    def extract_object(parse_tree):
        name = extract('person_concrete', parse_tree)
        return {'name': name}

    def update_kb(self, intent, object_):
        """ Adds data to the KB that may be relevant to this query. """
        if 'name' in object_:
            name = object_['name']
            credits = get_credits_by_name(name)
            self.kb[name] = credits

    def query_kb(self, intent, object_, modifier=None, frame=None):
        """ Makes a query to the knowledge base. """
        if intent[0] == 'CREDITS':
            if 'name' in object_:
                name = object_['name']
                credits = self.kb[name]
                if intent[1] == 'COUNT_OF':
                    return len(credits)

    def generate_summary(self, intent, object_, result):
        if intent[0] == 'CREDITS':
            if intent[1] == 'COUNT_OF':
                name = object_['name'].title()
                return '{0} was in {1} movies.'.format(name, result)


if __name__ == "__main__":
    print MovieService().go({
        'query': 'How many movies was tom hanks in?'
    })
