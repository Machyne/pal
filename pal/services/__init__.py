from pal.services.dictionary_service import DictionaryService
from pal.services.directory_service import DirectoryService
from pal.services.bonapp_service import BonAppetitService
from pal.services.omdb_service import OMDBService
from pal.services.weather_service import WeatherService

_SERVICES = {
    'dictionary': DictionaryService('dictionary'),
    'directory': DirectoryService('stalkernet'),
    'ombd': OMDBService('movie'),
    'weather': WeatherService('weather'),
    'food': BonAppetitService('bonapp'),
}


def get_all_service_names():
    return _SERVICES.keys()


def get_service_by_name(name):
    if name in _SERVICES:
        return _SERVICES[name]
