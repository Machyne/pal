#!/usr/bin/env python
# coding: utf-8
#
# An API to the Bon Appetit food service data
#
# Author: Alex Simonides and Ken Schiller
# TODO:
# - Add support for caching data with pickle
# - Decide on a naming scheme for cached data
# - Implement a way to clear the cache as it becomes irrelevant
# - Add a CI job to cache data every morning/evening


# import datetime
import json
import re
import requests

from helper import filter_dict_by_keys

# Constants for scraping the cafe pages
_CAFE_URL = 'http://carleton.cafebonappetit.com/cafe/{cafe_name}/{date}/'
_CAFE_NAMES = ['burton', 'east-hall', 'sayles-hill-cafe', 'weitz-cafe']
_RE_NAME = r'Bamco.current_cafe\s+=\s+(?:[^;]+)name:\s+\'(.*?)\'(?:[^;]+);'
_RE_MENU = r'Bamco.menu_items\s+=\s+([^;]+);'
_RE_DAYPARTS = r'Bamco.dayparts\[\'(\d+)\'\]\s+=\s+([^;]+);'

# Constants for parsing Bamco.menu_items
_BASE_FIELDS = [u'id', u'label']
_MENU_FIELDS = _BASE_FIELDS + [u'description', u'cor_icon', u'station']
_MENU_REPLACEMENTS = (
    (re.compile(r' (\([^G]?G?\))'), ""),
    (re.compile(r'\s+'), " ")
)
_MEAL_FIELDS = _BASE_FIELDS + [u'stations', u'starttime', u'endtime']
_MEAL_STATION_FIELDS = _BASE_FIELDS + [u'items']


def _get_page_for_cafe(cafe_name, day):
    ''' Returns the HTML page for the given cafe and date.
    '''
    url = _CAFE_URL.format(cafe_name=cafe_name, date=day.isoformat())
    response = requests.get(url)
    return response.text


def _get_raw_data_for_cafe(cafe_name, day):
    ''' Returns the name, menu, and dayparts for the given cafe and date.
    '''
    page = _get_page_for_cafe(cafe_name, day)
    name_matches = re.findall(_RE_NAME, page)
    name = name_matches[0]
    menu_matches = re.findall(_RE_MENU, page)
    menu = json.loads(menu_matches[0])
    dayparts = {}
    dayparts_matches = re.findall(_RE_DAYPARTS, page)
    for match in dayparts_matches:
        part_num, dict_ = match
        dayparts[int(part_num)] = json.loads(dict_)
    return name, menu, dayparts


def get_menu_for_cafe(cafe_name, day):
    ''' Returns a cleaned version of the menu info for the given cafe and date.
    '''
    _, menu, _ = _get_raw_data_for_cafe(cafe_name, day)
    if not menu:
        return None
    for food_id in menu:
        info = filter_dict_by_keys(menu[food_id], _MENU_FIELDS)
        for regex, new in _MENU_REPLACEMENTS:
            info[u'description'] = regex.sub(new, info[u'description'])
            info[u'label'] = regex.sub(new, info[u'label'])
        menu[food_id] = info
    return menu


def get_meals_for_cafe(cafe_name, day):
    ''' Returns a cleaned version of the meals info for the given cafe and date.
    '''
    menu = get_menu_for_cafe(cafe_name, day)
    _, _, dayparts = _get_raw_data_for_cafe(cafe_name, day)
    if not dayparts:
        return dayparts
    dayparts = _use_labels_as_keys(dayparts)
    for meal_name in dayparts:
        info = filter_dict_by_keys(dayparts[meal_name], _MEAL_FIELDS)
        meal_stations = _use_labels_as_keys(info[u'stations'])
        for stat_name in meal_stations:
            stat_info = filter_dict_by_keys(meal_stations[stat_name],
                                            _MEAL_STATION_FIELDS)
            if u'items' in stat_info:
                items = stat_info[u'items']
                stat_info[u'items'] = [menu[eid]
                                       for eid in items
                                       if type(eid) == unicode]
            meal_stations[stat_name] = stat_info
        info[u'stations'] = meal_stations
        dayparts[meal_name] = info
    return dayparts


def _use_labels_as_keys(collection):
    ''' Given a list or dict of items, returns a dict with items' labels for keys.
    '''
    if type(collection) == dict:
        return {all_info.pop(u'label'): all_info
                for (old_id, all_info) in collection.iteritems()}
    elif type(collection) == list:
        return {all_info.pop(u'label'): all_info
                for all_info in collection}


# def profile(runs=1):
#     deltas = []
#     for i in range(runs):
#         start = datetime.datetime.now()
#         bon_api = BonAPI()
#         bon_api.get_data("east-hall", datetime.date.today())
#         delta = datetime.datetime.now() - start
#         print delta
#         deltas.append(delta)
#     print "Average: ", (sum(deltas, datetime.timedelta())/runs)


# if __name__ == '__main__':
#     bon_api = BonAPI()
#     pprint(bon_api.get_data("east-hall",
#                             datetime.date.today()))
