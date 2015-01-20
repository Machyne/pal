from pal.services.directory_service import DirectoryService
from pal.services.omdb_service import OMDBService
from pal.services.weather_service import WeatherService

_SERVICES = {
    'directory': DirectoryService('stalkernet'),
    'ombd': OMDBService('movie'),
    'weather': WeatherService('weather')
}


def get_all_service_names():
    return _SERVICES.keys()


def get_service_by_name(name):
    if name in _SERVICES:
        return _SERVICES[name]
