from datetime import datetime
import string

import requests

from config import TMDB_KEY
from pal.grammars.parser import normalize_string


_BASE_URL = 'http://api.themoviedb.org/3/'
_PERSON_BY_NAME = 'search/person?query={name}&api_key={api_key}'
_MOVIE_BY_TITLE = 'search/movie?query={title}&api_key={api_key}'
_CREDITS_BY_PERSON_ID = 'person/{id}/movie_credits?api_key={api_key}'
_IMAGE_BASE_URL = 'http://image.tmdb.org/t/p/w500/'

# The "Knowledge Base" (KB)
_PEOPLE = {}   # TMDBPerson objects indexed by name
_MOVIES = {}   # TMDBMovie objects indexed by title
_CREDITS = {}  # TMDBCredit objects indexed by (name, title, role, year)


def to_ascii(s):
    return filter(lambda x: x in string.printable, s)


def compare_names(reference, query):
    """ Compares strings after stripping, lowering, and removing punctuation.
    """
    return normalize_string(reference).contains(normalize_string(query))


def compare_titles(reference, query):
    """ Compares strings after stripping, lowering, and removing punctuation.
    """
    return normalize_string(reference).startswith(normalize_string(query))


class TMDBMovie(object):
    def __init__(self, movie_dict):
        self.title = to_ascii(movie_dict['title'])
        self.date_ = datetime.strptime(movie_dict['release_date'], '%Y-%m-%d') \
            if 'release_date' in movie_dict and movie_dict['release_date'] \
            else None
        self.image_url = _IMAGE_BASE_URL + movie_dict['poster_path'] \
            if 'poster_path' in movie_dict and movie_dict['poster_path'] \
            else None

    @property
    def year(self):
        return self.date_.year if self.date_ else None

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.year)


class TMDBPerson(object):
    def __init__(self, person_dict):
        self.name = to_ascii(person_dict['name'])
        self.id = person_dict['id']
        self.image_url = _IMAGE_BASE_URL + person_dict['profile_path'] \
            if 'poster_path' in person_dict and person_dict['poster_path'] \
            else None

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.image_url)


class TMDBCredit(object):
    def __init__(self, name, title, role, year):
        self.name = name
        self.title = title
        self.role = role
        self.year = year

    def __str__(self):
        return '{0}, {1} ({2}, {3})'.format(self.name, self.title,
                                            self.role, self.year)


def _normalize_role(role):
    """ Maps a TMDB `job` field to one of set of standardized role names. """
    if role.lower() in ['director']:
        return 'director'
    if role.lower() in ['author', 'screenplay', 'story', 'writer']:
        return 'writer'
    if role.lower() in ['producer', 'produzent']:
        return 'producer'
    return role


def _get(endpoint, **params):
    """ Makes a request with params to an endpoint, returns dictionary """
    params['api_key'] = TMDB_KEY
    response = requests.get(_BASE_URL + endpoint.format(**params))
    return response.json()


def get_person_by_name(name):
    """ Returns a TMDBPerson for the first search result matching `name`. """
    if name in _PEOPLE:
        return _PEOPLE[name]
    response = _get(_PERSON_BY_NAME, name=name)
    if 'results' in response:
        results = response['results']
        if results:
            person = TMDBPerson(results[0])
            _PEOPLE[name] = person
            return person
    return None


def get_movie_by_title(title):
    """ Returns a TMDBMovie for the first search result matching `title`. """
    if title in _MOVIES:
        return _MOVIES[title]
    response = _get(_MOVIE_BY_TITLE, title=title)
    if 'results' in response:
        results = response['results']
        if results:
            movie = TMDBMovie(results[0])
            _MOVIES[title] = movie
            return movie
    return None


def load_movie_for_title(title):
    get_movie_by_title(title)


def load_credits_for_name(name):
    person = get_person_by_name(name)
    if not person:
        return []
    id_ = person.id
    results = _get(_CREDITS_BY_PERSON_ID, id=id_)
    if 'cast' in results:
        for movie_dict in results['cast']:
            movie = TMDBMovie(movie_dict)
            params = (name, movie.title, 'actor', movie.year)
            _CREDITS[params] = TMDBCredit(*params)
            _MOVIES[movie.title] = movie
    if 'crew' in results:
        for movie_dict in results['crew']:
            role = _normalize_role(movie_dict['job'])
            movie = TMDBMovie(movie_dict)
            params = (name, movie.title, role, movie.year)
            _CREDITS[params] = TMDBCredit(*params)
            _MOVIES[movie.title] = movie


def get_credits(name=None, title=None, role=None, year=None):
    def filter_(credit):
        if name and not compare_titles(credit.name, name):
            return False
        if title and not compare_titles(credit.title, title):
            return False
        if role and credit.role != role:
            return False
        if year and credit.year != year:
            return False
        return True
    # print 'get credits: ({0}, {1}, {2}, {3})'.format(name, title, role, year)
    credits = _CREDITS.itervalues()
    return filter(filter_, credits)


def get_movies(name=None, title=None, role=None, year=None):
    def filter_(movie):
        if name and not compare_names(movie.name, name):
            return False
        if title and not compare_titles(movie.title, title):
            return False
        if role and movie.role != role:
            return False
        if year and movie.year != year:
            return False
        return True
    if title:
        movies = (_MOVIES[title] if title in _MOVIES else None)
    else:
        movies = _MOVIES.itervalues()
    if name:
        movies = filter(lambda x: not not _CREDITS[name][x.title].keys(),
                        movies)
    if year:
        movies = filter(lambda x: x.date_.year == year, movies)
    # TODO: WTF?
    if isinstance(movies, TMDBMovie):
        return [movies]
    return movies


if __name__ == '__main__':
    # get_movie_names_for_person('Tom Hanks')
    # for c in get_credits_by_name('Wes Anderson'):
        # print c
    # print get_person_by_name('tom hanks')
    load_credits_for_name('Tom Hanks')
    print len(get_credits(role='actor'))
