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


import json
import re

import requests

from api import DataNotAvailableException
from utils import filter_dict_by_keys

# Constants for scraping the cafe pages
CAFE_NAMES = ['burton', 'east-hall', 'sayles-hill-cafe', 'weitz-cafe']
_CAFE_URL = 'http://carleton.cafebonappetit.com/cafe/{cafe_name}/{date}/'
_RE_NAME = r'Bamco.current_cafe\s+=\s+(?:[^;]+)name:\s+\'(.*?)\'(?:[^;]+);'
_RE_MENU = r'Bamco.menu_items\s+=\s+([^;]+);'
_RE_DAYPARTS = r'Bamco.dayparts\[\'(\d+)\'\]\s+=\s+([^;]+);'

# Constants for parsing Bamco.menu_items
_BASE_FIELDS = [u'id', u'label']
_MENU_FIELDS = _BASE_FIELDS + [u'description', u'cor_icon']
_MENU_REPLACEMENTS = (
    (re.compile(r' (\([^G]?G?\))'), ""),
    (re.compile(r'\s+'), " ")
)
_MEAL_FIELDS = _BASE_FIELDS + [u'stations', u'time_formatted']
_MEAL_STATION_FIELDS = _BASE_FIELDS + [u'items']


def _get_page_for_cafe(cafe_name, date_):
    """ Returns the HTML page for the given cafe and date."""
    url = _CAFE_URL.format(cafe_name=cafe_name, date=date_.isoformat())
    response = requests.get(url, timeout=1.0)
    return response.text


def _get_raw_data_from_page(page):
    """ Scrapes the name, menu, and dayparts from the given page."""
    name_matches = re.findall(_RE_NAME, page)
    name = name_matches[0] if name_matches else None
    menu_matches = re.findall(_RE_MENU, page)
    dishes = json.loads(menu_matches[0]) if menu_matches else None
    dayparts = {}
    dayparts_matches = re.findall(_RE_DAYPARTS, page)
    if dayparts_matches:
        for match in dayparts_matches:
            part_num, dict_ = match
            dayparts[int(part_num)] = json.loads(dict_)
    else:
        dayparts = None
    return name, dishes, dayparts


def _get_raw_data_for_cafe(cafe_name, day):
    """ Returns the name, menu, and dayparts for the given cafe and date."""
    page = _get_page_for_cafe(cafe_name, day)
    return _get_raw_data_from_page(page)


def _clean_menu(menu):
    """ Returns a cleaned version of the given menu info for dishes."""
    if not menu:
        return None
    for food_id in menu:
        info = filter_dict_by_keys(menu[food_id], _MENU_FIELDS)
        for regex, new in _MENU_REPLACEMENTS:
            info[u'description'] = regex.sub(new, info[u'description'])
            info[u'label'] = regex.sub(new, info[u'label'])
        menu[food_id] = info
    return menu


def _clean_meals_and_merge_dishes(dayparts, dishes):
    """ Takes in the cleaned menu and messy dayparts, cleans the dayparts then
        merges the dishes into the right stations in the meals.
    """
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
                # Put all the dishes served at this station into the dict
                items = stat_info[u'items']
                stat_info[u'items'] = [dishes[eid]
                                       for eid in items
                                       if type(eid) == unicode]
            meal_stations[stat_name] = stat_info
        info[u'stations'] = meal_stations
        dayparts[meal_name] = info
    return dayparts


def get_meals_for_cafe(cafe_name, date_):
    """ Returns a cleaned version of the meals info for
        the given cafe and date.
    """
    page = _get_page_for_cafe(cafe_name, date_)
    _, menu, dayparts = _get_raw_data_from_page(page)
    if menu is None or dayparts is None:
        raise DataNotAvailableException(
            "Data was not available for {} on {}".format(cafe_name,
                                                         date_.weekday()))
    dishes = _clean_menu(menu)
    meals = _clean_meals_and_merge_dishes(dayparts, dishes)
    return meals


def _use_labels_as_keys(collection):
    """ Given a list or dict of items, returns a dict
        with each item's 'label' value as the item's key.
    """
    if type(collection) == dict:
        return {all_info.pop(u'label'): all_info
                for (old_id, all_info) in collection.iteritems()}
    elif type(collection) == list:
        return {all_info.pop(u'label'): all_info
                for all_info in collection}

if __name__ == '__main__':
    from datetime import date
    print get_meals_for_cafe('burton', date.today())
