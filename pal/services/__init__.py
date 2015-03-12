#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from pal.services.base_service import wrap_response
from pal.services.bonapp_service import BonAppService
from pal.services.dictionary_service import DictionaryService
from pal.services.directory_service import DirectoryService
from pal.services.dominos_service import DominosService
from pal.services.facebook_service import FacebookService
from pal.services.joke_service import JokeService
from pal.services.movie_service import MovieService
from pal.services.ultralingua_service import UltraLinguaService
from pal.services.wa_service import WAService
from pal.services.weather_service import WeatherService
from pal.services.yelp_service import YelpService


# A service class is "plugged-in" once its been added to this list,
# which should be kept alphabetized for developer convenience
_SERVICE_CLASSES = [
    BonAppService,
    DictionaryService,
    DirectoryService,
    DominosService,
    FacebookService,
    JokeService,
    MovieService,
    UltraLinguaService,
    WAService,
    WeatherService,
    YelpService,
]
_SERVICES = {cls.short_name(): cls() for cls in _SERVICE_CLASSES}


@wrap_response
def no_response():
    return ('ERROR', "Sorry, I'm not sure what you mean.")


def get_all_service_names():
    return _SERVICES.keys()


def get_service_by_name(name):
    if name in _SERVICES:
        return _SERVICES[name]
