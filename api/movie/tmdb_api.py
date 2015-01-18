from datetime import datetime

import requests

from config import TMDB_KEY


_BASE_URL = 'http://api.themoviedb.org/3/'
_PERSON_BY_NAME = 'search/person?query={name}&api_key={api_key}'
_CREDITS_BY_PERSON_ID = 'person/{id}/movie_credits?api_key={api_key}'
_IMAGE_BASE_URL = 'http://image.tmdb.org/t/p/w500/'
_PEOPLE = {}
_MOVIES = {}


class TMDBMovie(object):
    def __init__(self, movie_dict):
        self.title = movie_dict['title']
        self.date_ = datetime.strptime(movie_dict['release_date'], '%Y-%m-%d')
        self.image_url = _IMAGE_BASE_URL + movie_dict['poster_path']

    def __str__(self):
        return '{0} ({1})'.format(self.title, self.date_.year)


class TMDBPerson(object):
    def __init__(self, person_dict):
        self.name = person_dict['name']
        self.id = person_dict['id']
        self.image_url = _IMAGE_BASE_URL + person_dict['profile_path']

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.image_url)


class TMDBCredit(object):
    def __init__(self, movie_id, role):
        self.movie_id = movie_id
        self.role = role

    def __str__(self):
        return '{0}, {1}'.format(self.role, _MOVIES[self.movie_id])


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
    if name not in _PEOPLE:
        results = _get(_PERSON_BY_NAME, name=name)['results']
        if results:
            person = TMDBPerson(results[0])
            _PEOPLE[name] = person
    return _PEOPLE[name] if name in _PEOPLE else None


def get_credits_by_name(name):
    """ Returns a list of unique TMDBCredits for the TMDBPerson `person` """
    person = get_person_by_name(name)
    id_ = person.id
    results = _get(_CREDITS_BY_PERSON_ID, id=id_)
    credits_set = set()
    if 'cast' in results:
        for movie_dict in results['cast']:
            movie_id = movie_dict['id']
            if movie_id not in _MOVIES:
                _MOVIES[movie_id] = TMDBMovie(movie_dict)
            credit = movie_id, 'actor'
            credits_set.add(credit)
    if 'crew' in results:
        for movie_dict in results['crew']:
            movie_id = movie_dict['id']
            if movie_id not in _MOVIES:
                _MOVIES[movie_id] = TMDBMovie(movie_dict)
            role = _normalize_role(movie_dict['job'])
            credit = movie_id, role
            credits_set.add(credit)
    return [TMDBCredit(*c) for c in credits_set]


if __name__ == '__main__':
    # get_movie_names_for_person('Tom Hanks')
    for c in get_credits_by_name('Wes Anderson'):
        print c
