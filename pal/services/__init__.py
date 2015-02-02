from pal.services.bonapp_service import BonAppService
from pal.services.dictionary_service import DictionaryService
from pal.services.directory_service import DirectoryService
from pal.services.movie_service import MovieService
from pal.services.service import wrap_response
from pal.services.weather_service import WeatherService


_SERVICE_CLASSES = [DictionaryService, DirectoryService, MovieService,
                    WeatherService, BonAppService]
_SERVICES = {cls.short_name(): cls() for cls in _SERVICE_CLASSES}


@wrap_response
def no_response():
    return ('ERROR', "Sorry, I'm not sure what you mean.")


def get_all_service_names():
    return _SERVICES.keys()


def get_service_by_name(name):
    if name in _SERVICES:
        return _SERVICES[name]
