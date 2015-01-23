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

from utils import filter_dict_by_keys

# Constants for scraping the cafe pages
_CAFE_URL = 'http://carleton.cafebonappetit.com/cafe/{cafe_name}/{date}/'
_CAFE_NAMES = ['burton-hall', 'east-hall', 'sayles-hill-cafe', 'weitz-cafe']
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
    """ Returns the HTML page for the given cafe and date."""
    url = _CAFE_URL.format(cafe_name=cafe_name, date=day.isoformat())
    response = requests.get(url)
    return response.text


def _get_raw_data_for_cafe(cafe_name, day):
    """ Returns the name, menu, and dayparts for the given cafe and date."""
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
    """ Returns a cleaned version of the menu info for
        the given cafe and date.
    """
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
    """ Returns a cleaned version of the meals info for
        the given cafe and date.
    """
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
    """ Given a list or dict of items, returns a dict
        with items' labels for keys.
    """
    if type(collection) == dict:
        return {all_info.pop(u'label'): all_info
                for (old_id, all_info) in collection.iteritems()}
    elif type(collection) == list:
        return {all_info.pop(u'label'): all_info
                for all_info in collection}


FAKE_DATA = {
    u'current_cafe': {
        u'id': 245.0,
        u'name': u'East Hall'},
    u'dayparts': {
        u'Breakfast': {
            u'endtime': u'10:00',
            u'id': u'1',
            u'starttime': u'07:30',
            u'stations': {
                u'Breakfast': {
                    u'id': u'5774',
                    u'items': [{
                        u'cor_icon': {
                            u'1': u'vegetarian',
                            u'9': (
                                u'Made without Gluten-'
                                u'Containing Ingredients')},
                        u'description': u'',
                        u'id': u'2941794',
                        u'label': (u'Scrambled Eggs, '
                                   u'Scrambled Eggs with Cheese'),
                        u'station': u'Breakfast'},
                        {
                        u'cor_icon': {
                            u'1': u'vegetarian',
                            u'9': (
                                u'Made without Gluten-'
                                u'Containing Ingredients')},
                        u'description': u'',
                        u'id': u'2941798',
                        u'label': u'Bacon, Vegetarian Sausage',
                        u'station': u'Breakfast'}]},
                u'Cucina': {
                    u'id': u'773',
                    u'items': [{
                        u'cor_icon': {
                            u'1': u'vegetarian',
                            u'9': (
                                u'Made without Gluten-'
                                u'Containing Ingredients')},
                        u'description': u'',
                        u'id': u'2969190',
                        u'label': u'Sweet Potato Quiche Cups',
                        u'station': u'Cucina'}]},
                u'Wild Thymes': {
                    u'id': u'777',
                    u'items': [{
                        u'cor_icon': {
                            u'4': u'vegan'},
                        u'description': u'',
                        u'id': u'2969185',
                        u'label': (
                            u'Roasted Corn and Chipotle Tofu Breakfast '
                            u'Burrito with Saut\xe9ed Peppers'),
                        u'station': u'Wild Thymes'}]}}},
        u'Dinner': {
            u'endtime': u'19:00',
            u'id': u'4',
            u'starttime': u'16:45',
            u'stations': {
                u'American Regional': {
                    u'id': u'774',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': (
                            u'Sloppy Joes, Grilled Chicken Breast, '
                            u'House Edamame Burger, House Chipotle French'
                            u' Fries, Saut\xe9ed Bell Peppers, '
                            u'Saut\xe9ed Onions, Saut\xe9ed Mushrooms '
                            u'Roasted Parsnips(WB)'),
                        u'id': u'2969173',
                        u'label': u'Hot Sandwiches etc',
                        u'station': u'American Regional'}]},
                u'Chopsticks and Woks': {
                    u'id': u'776',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': u'',
                        u'id': u'2969141',
                        u'label': (u'Steamed Brown Rice,'
                                   u'Steamed White Rice'),
                        u'station': u'Chopsticks and Woks'},
                        {
                            u'cor_icon': {
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                            u'description': u'',
                            u'id': u'2969146',
                            u'label': (u'Five Spice Chicken Stir-fry with '
                                       u'Carrots and Celery '),
                            u'station': u'Chopsticks and Woks'},
                        {
                            u'cor_icon': {
                                u'4': u'vegan',
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                            u'description': u'',
                            u'id': u'2969147',
                            u'label': u'Stir-fried Bok Choy and Cabbage ',
                            u'station': u'Chopsticks and Woks'}]},
                u'Cucina': {
                    u'id': u'773',
                    u'items': [{u'cor_icon': [],
                                u'description': (
                                u'Hummus Pizza with Broccoli and Cheddar,'
                                u' Italian Sausage Pizza, "Hasting Dairy'
                                u' Co-Op" Four Cheese(LC), Made Without '
                                u'Gluten Pizza Available upon Request'),
                                u'id': u'2969132',
                                u'label': u'Pizza'},
                               {u'cor_icon': [],
                                u'description': (u'Pasta, Sauce Marinara, '
                                                 u'Alfredo Sauce'),
                                u'id': u'2941812',
                                u'label': (u"Chef's choice Pasta with choice "
                                           u"of sauce"),
                                u'station': u'Cucina'},
                               {u'cor_icon': [],
                                u'description': u'',
                                u'id': u'2969121',
                                u'label': (u'Beef Chow Mein or Vegetarian '
                                           u'Chow Mein'),
                                u'station': u'Cucina'},
                               {u'cor_icon': {
                                   u'4': u'vegan',
                                   u'9': (
                                       u'Made without Gluten-'
                                       u'Containing Ingredients')},
                                u'description': u'',
                                u'id': u'2969159',
                                u'label': (u'Burgundy Braised Tofu Stroganoff '
                                           u'with Mushrooms'),
                                u'station': u'Cucina'},
                               {u'cor_icon': [],
                                u'description': u'',
                                u'id': u'2969165',
                                u'label': (u'Tomato Lasagna with Italian '
                                           u'Sausage and Beef'),
                                u'station': u'Cucina'}]},
                    u'Cucina Pizza': {
                        u'id': u'775',
                        u'items': [{
                            u'cor_icon': [],
                            u'description': (
                                u'Hummus Pizza with Broccoli and Cheddar,'
                                u' Italian Sausage Pizza, "Hasting Dairy'
                                u' Co-Op" Four Cheese(LC), Made Without '
                                u'Gluten Pizza Available upon Request'),
                            u'id': u'2969132',
                            u'label': u'Pizza'}]},
                    u'Soup': {
                        u'id': u'5775',
                        u'items': [{
                            u'cor_icon': {
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                                u'description': u'',
                                u'id': u'2969102',
                                u'label': u'Santa Fe Chicken and Rice',
                                u'station': u'Soup'},
                            {
                                u'cor_icon': {
                                    u'4': u'vegan',
                                    u'9': (
                                        u'Made without Gluten-'
                                        u'Containing Ingredients')},
                                u'description': u'',
                                u'id': u'2969103',
                                u'label': u'Ginger Carrot and Orange Soup ',
                                u'station': u'Soup'}]},
                    u'Wild Thymes': {
                        u'id': u'777',
                        u'items': [{
                            u'cor_icon': {
                                u'4': u'vegan',
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                            u'description': u'',
                            u'id': u'2969179',
                            u'label': u"Shepard's Pie",
                            u'station': u'Wild Thymes'}]}}},
        u'Lunch': {
            u'endtime': u'14:00',
            u'id': u'3',
            u'starttime': u'11:30',
            u'stations': {
                u'American Regional': {
                    u'id': u'774',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': (
                            u'Sloppy Joes, Grilled Chicken Breast, '
                            u'House Edamame Burger, House Chipotle French'
                            u' Fries, Saut\xe9ed Bell Peppers, '
                            u'Saut\xe9ed Onions, Saut\xe9ed Mushrooms '
                            u'Roasted Parsnips(WB)'),
                        u'id': u'2969173',
                        u'label': u'Hot Sandwiches etc',
                        u'station': u'American Regional'}]},
                u'Chopsticks and Woks': {
                    u'id': u'776',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': u'',
                        u'id': u'2969141',
                        u'label': (u'Steamed Brown Rice, '
                                   u'Steamed White Rice'),
                        u'station': u'Chopsticks and Woks'},
                        {
                            u'cor_icon': {
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                            u'description': u'',
                            u'id': u'2969146',
                            u'label': (u'Five Spice Chicken Stir-fry with '
                                       u'Carrots and Celery '),
                            u'station': u'Chopsticks and Woks'},
                        {
                            u'cor_icon': {
                                u'4': u'vegan',
                                u'9': (
                                    u'Made without Gluten-'
                                    u'Containing Ingredients')},
                            u'description': u'',
                            u'id': u'2969147',
                            u'label': u'Stir-fried Bok Choy and Cabbage ',
                            u'station': u'Chopsticks and Woks'}]},
                u'Cucina': {
                    u'id': u'773',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': (u'Pasta, Sauce Marinara, '
                                         u'Alfredo Sauce'),
                        u'id': u'2941812',
                        u'label': (u"Chef's choice Pasta with choice "
                                   u"of sauce"),
                        u'station': u'Cucina'},
                        {
                            u'cor_icon': [],
                            u'description': u'',
                            u'id': u'2969121',
                            u'label': (u'Beef Chow Mein or Vegetarian '
                                       u'Chow Mein'),
                            u'station': u'Cucina'}]},
                u'Cucina Pizza': {
                    u'id': u'775',
                    u'items': [{
                        u'cor_icon': [],
                        u'description': (
                            u'Hummus Pizza with Broccoli and Cheddar,'
                            u' Italian Sausage Pizza, "Hasting Dairy'
                            u' Co-Op" Four Cheese(LC), Made Without '
                            u'Gluten Pizza Available upon Request'),
                        u'id': u'2969132',
                        u'label': u'Pizza',
                        u'station': u'Cucina Pizza'}]},
                u'Soup': {
                    u'id': u'5775',
                    u'items': [{
                        u'cor_icon': {
                            u'9': (
                                u'Made without Gluten-'
                                u'Containing Ingredients')},
                        u'description': u'',
                        u'id': u'2969102',
                        u'label': u'Santa Fe Chicken and Rice',
                        u'station': u'Soup'},
                        {
                        u'cor_icon': {
                            u'4': u'vegan',
                            u'9': (
                                u'Made without Gluten-'
                                u'Containing Ingredients')},
                        u'description': u'',
                        u'id': u'2969103',
                        u'label': u'Ginger Carrot and Orange Soup ',
                        u'station': u'Soup'}]}}}}}


class BonAPI(object):

    def get_data(self, cafe, date):
        return FAKE_DATA

# if __name__ == '__main__':
#     bon_api = BonAPI()
#     pprint(bon_api.get_data("east-hall",
#                             datetime.date.today()))
