# A service for movie info

from api.movie.tmdb_api import get_credits
from api.movie.tmdb_api import get_movies
from api.movie.tmdb_api import load_credits_for_name
from api.movie.tmdb_api import load_movie_for_title
from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parse
from pal.services.base_service import Service
from pal.services.base_service import wrap_response


def verb_phrase_from_role(role):
    if not role:
        verb = 'been'
    elif role == 'writer':
        verb = 'wrote'
    else:
        verb = role[:-2] + 'ed'
    if verb in ['acted', 'been']:
        return 'has ' + verb + ' in'
    return 'has ' + verb


class MovieService(Service):

    def __init__(self):
        self.grammar = get_grammar_for_service(self.__class__.short_name())
        self.cached_parse = None

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        query = params['query']
        parse_ = parse(query, self.grammar)
        self.cached_parse = (query, parse_)
        # FIXME: Right now 61 is returned due to conflicts with hill climbed
        # values and the grammar parses.
        return 61 if parse_ else 0

    @wrap_response
    def go(self, params):
        query = params['query']
        if self.cached_parse and self.cached_parse[0] == query:
            parse_tree = self.cached_parse[1]
        else:
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
        if extract(parse_tree, 'person_to_movie_yes_no'):
            intent = ('CREDITS', 'BOOLEAN_OF')
        elif extract(parse_tree, 'wh_count'):
            intent = ('CREDITS', 'COUNT_OF')
        elif extract(parse_tree, 'movie_to_person_question') \
            or extract(parse_tree, 'movie_to_person_description'):
            intent = ('CREDITS', 'MOVIES_OF')
        elif extract(parse_tree, 'person_to_movie_question'):
            intent = ('CREDITS', 'PEOPLE_OF')
        elif extract(parse_tree, 'year_of_movie'):
            intent = ('MOVIES', 'YEAR_OF')
        return intent

    @staticmethod
    def extract_role(parse_tree):
        if extract(parse_tree, 'actor_word') \
            or extract(parse_tree, 'movie_act_on_person'):
            return 'actor'
        if extract(parse_tree, 'direction_word') \
            or extract(parse_tree, 'direct'):
            return 'director'
        if extract(parse_tree, 'producer_word') \
            or extract(parse_tree, 'produce'):
            return 'producer'
        if extract(parse_tree, 'writer_word') \
            or extract(parse_tree, 'write'):
            return 'writer'
        return ''

    @staticmethod
    def extract_object(parse_tree):
        name = extract(parse_tree, 'name')
        title = extract(parse_tree, 'title')
        year = extract(parse_tree, 'year')
        role = MovieService.extract_role(parse_tree)
        return {'name': name, 'title': title, 'role': role, 'year': year}

    def update_kb(self, intent, object_):
        """ Adds data to the KB that may be relevant to this query. """
        if object_['name']:
            load_credits_for_name(object_['name'])
        if object_['title']:
            load_movie_for_title(object_['title'])

    def query_kb(self, intent, object_, modifier=None, frame=None):
        """ Makes a query to the knowledge base, and returns a string
            representation of the result. """
        if intent[0] == 'CREDITS':
            credits = get_credits(**object_)
            if intent[1] == 'BOOLEAN_OF':
                return 'Yes' if credits else 'No'
            if intent[1] == 'COUNT_OF':
                unique_titles = {credit.title for credit in credits}
                return str(len(unique_titles))
            if intent[1] == 'MOVIES_OF':
                return ', '.join(sorted({credit.title.title() for credit in credits}))
            if intent[1] == 'PEOPLE_OF':
                return ', '.join(sorted({credit.name.title() for credit in credits}))
        elif intent[0] == 'MOVIES':
            movies = get_movies(**object_)
            if intent[1] == 'YEAR_OF':
                return movies[0].year

    def generate_summary(self, intent, object_, result):
        data = {
            'name': object_['name'].title(),
            'title': object_['title'].title(),
            'verb_phrase': verb_phrase_from_role(object_['role']),
            'result': result
        }
        SUMMARY_TEMPLATES = {
            ('CREDITS', 'BOOLEAN_OF'): '{result}.',
            ('CREDITS', 'COUNT_OF'): '{name} {verb_phrase} {result} movies.',
            ('CREDITS', 'MOVIES_OF'): '{result}.',
            ('CREDITS', 'PEOPLE_OF'): '{result}.',
            ('MOVIES', 'YEAR_OF'): '{title} was in the year {result}.'
        }
        if intent in SUMMARY_TEMPLATES:
            return SUMMARY_TEMPLATES[intent].format(**data)


if __name__ == "__main__":
    from pal.test import parse_examples
    examples = parse_examples()
    i = 0
    for example in examples['movie']:
        if i > 10:
            pass
        i += 1
        print example
        print MovieService().go({
            'query': example
        })['summary']
        print
