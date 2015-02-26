# A service for movie info

from api.movie.tmdb_api import get_credits
from api.movie.tmdb_api import get_movies
from api.movie.tmdb_api import load_credits_for_name
from api.movie.tmdb_api import load_movie_for_title
from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parse
from pal.services.service import Service
from pal.services.service import wrap_response


class MovieService(Service):

    def __init__(self):
        self.grammar = get_grammar_for_service(self.__class__.short_name())
        self.cached_parse = None

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        query = params['query']

        # TODO: shouldn't have to do this
        if query[-1] == '?':
            query = query[:-1]

        parse_ = parse(query, self.grammar)
        self.cached_parse = (query, parse_)
        return 75 if parse_ else 0

    @wrap_response
    def go(self, params):
        query = params['query']

        # TODO: shouldn't have to do this
        if query[-1] == '?':
            query = query[:-1]

        if self.cached_parse and self.cached_parse[0] == query:
            parse_tree = self.cached_parse[1]
        else:
            parse_tree = parse(query, self.grammar)

        print parse_tree
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
        name = extract('person_concrete', parse_tree)
        title = extract('movie_concrete', parse_tree)
        if title:
            intent = ('MOVIES', 'YEAR_OF')
        if name:
            intent = ('CREDITS', 'COUNT_OF')
        if parse_tree[1][0][0] == 'aux':
            intent = (intent[0], 'BOOLEAN_OF')
        return intent

    @staticmethod
    def extract_object(parse_tree):
        name = extract('name', parse_tree)
        title = extract('title', parse_tree)
        year = extract('year', parse_tree)
        return {'name': name, 'title': title, 'year': year}

    def update_kb(self, intent, object_):
        """ Adds data to the KB that may be relevant to this query. """
        if object_['name']:
            load_credits_for_name(object_['name'])
        if object_['title']:
            load_movie_for_title(object_['title'])

    def query_kb(self, intent, object_, modifier=None, frame=None):
        """ Makes a query to the knowledge base. """
        if intent[0] == 'CREDITS':
            credits = get_credits(**object_)
            if intent[1] == 'BOOLEAN_OF':
                return not not credits
            if intent[1] == 'COUNT_OF':
                return len(credits)
        elif intent[0] == 'MOVIES':
            movies = get_movies(**object_)
            if intent[1] == 'YEAR_OF':
                return movies[0].date_.year

    def generate_summary(self, intent, object_, result):
        if intent[0] == 'CREDITS':
            name = object_['name'].title()
            if intent[1] == 'COUNT_OF':
                return '{0} was in {1} movies.'.format(name, result)
            if intent[1] == 'BOOLEAN_OF':
                return 'Yes.' if result else 'No.'
        elif intent[0] == 'MOVIES':
            if intent[1] == 'YEAR_OF':
                title = object_['title'].title()
                return '{0} was in the year {1}.'.format(title, result)


if __name__ == "__main__":
    print MovieService().go({
        'query': 'what year was the movie blade runner?'
    })
