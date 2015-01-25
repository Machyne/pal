from pal.services.dictionary_service import DictionaryService
from pal.services.directory_service import DirectoryService
from pal.services.bonapp_service import BonAppetitService
from pal.services.movies_service import MoviesService
from pal.services.weather_service import WeatherService


_SERVICE_CLASSES = [DictionaryService, DirectoryService, MoviesService,
                    WeatherService, BonAppetitService]
_SERVICES = {cls.name: cls() for cls in _SERVICE_CLASSES}


def get_all_service_names():
    return _SERVICES.keys()


def get_service_by_name(name):
    if name in _SERVICES:
        return _SERVICES[name]
