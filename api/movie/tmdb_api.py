from collections import defaultdict
from datetime import datetime

import requests

from config import TMDB_KEY


_BASE_URL = 'http://api.themoviedb.org/3/'
_PERSON_BY_NAME = 'search/person?query={name}&api_key={api_key}'
_MOVIE_BY_TITLE = 'search/movie?query={title}&api_key={api_key}'
_CREDITS_BY_PERSON_ID = 'person/{id}/movie_credits?api_key={api_key}'
_IMAGE_BASE_URL = 'http://image.tmdb.org/t/p/w500/'
_PEOPLE = {}  # TMDBPerson objects indexed by name
_MOVIES = {}  # TMDBMovie objects indexed by title
_CREDITS = set()  # Set of tuples (name, title, role)


class TMDBMovie(object):
    def __init__(self, movie_dict):
        self.title = movie_dict['title']
        self.date_ = datetime.strptime(movie_dict['release_date'], '%Y-%m-%d') \
            if 'release_date' in movie_dict and movie_dict['release_date'] \
            else None
        self.image_url = _IMAGE_BASE_URL + movie_dict['poster_path'] \
            if 'poster_path' in movie_dict and movie_dict['poster_path'] \
            else None

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.date_.year)


class TMDBPerson(object):
    def __init__(self, person_dict):
        self.name = person_dict['name']
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


def load_credits_for_name(name):
    person = get_person_by_name(name)
    if not person:
        return []
    id_ = person.id
    results = _get(_CREDITS_BY_PERSON_ID, id=id_)
    if 'cast' in results:
        for movie_dict in results['cast']:
            title = movie_dict['title']
            _CREDITS.add(TMDBCredit(name, title, 'actor'))
            _MOVIES[title] = TMDBMovie(movie_dict)
    if 'crew' in results:
        for movie_dict in results['crew']:
            title = movie_dict['title']
            role = _normalize_role(movie_dict['job'])
            _CREDITS.add(TMDBCredit(name, title, role))
            _MOVIES[title] = TMDBMovie(movie_dict)


def load_movie_for_title(title):
    get_movie_by_title(title)


def get_credits(name=None, title=None, role=None, year=None):
    def filter_(credit):
        if name and credit.name != name:
            return False
        if title and credit.title != title:
            return False
        if role and credit.role != role:
            return False
        if year and credit.year != year:
            return False
        return True
    return filter(filter_, _CREDITS)


def get_movies(name=None, title=None, role=None, year=None):
    def filter_(movie):
        if name and movie.name != name:
            return False
        if title and movie.title != title:
            return False
        if role and movie.role != role:
            return False
        if year and movie.year != year:
            return False
        return True
    if title:
        movies = [_MOVIES[title] if title in _MOVIES else None]
    else:
        movies = _MOVIES.values()
    if name:
        movies = filter(lambda x: not not _CREDITS[name][x.title].keys(),
                        movies)
    if year:
        movies = filter(lambda x: x.date_.year == year, movies)
    print movies
    return movies


if __name__ == '__main__':
    # get_movie_names_for_person('Tom Hanks')
    # for c in get_credits_by_name('Wes Anderson'):
        # print c
    # print get_person_by_name('tom hanks')
    load_credits_for_name('Tom Hanks')
    print len(get_credits(role='actor'))
