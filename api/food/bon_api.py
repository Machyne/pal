#!/usr/bin/env python
# coding: utf-8
#
# An API to the Bon Appetit food service data
#
# Author: Alex Simonides
# TODO:
# - Add support for caching data with pickle
# - Decide on a naming scheme for cached data
# - Implement a way to clear the cache as it becomes irrelevant
# - Add a CI job to cache data every morning/evening

import re
import datetime
from pprint import pprint

from ghost import Ghost
from ghost import TimeoutError


def filter_by_field_names(a_dict, field_names):
    """ Returns a copy of `a_dict` with only the fields in `field_names`"""
    if type(a_dict) != dict:
        return None
    return {key: value for (key, value) in a_dict.items()
            if key in field_names}


def filter_each_by_fields(iterable, field_names):
    """ Runs `filter_by_field_names()` on each dict in `iterable` and returns
        an object of the same type as `iterable`.
    """
    if type(iterable) == dict:
        return {key: filter_by_field_names(a_dict, field_names)
                for (key, a_dict) in iterable.items()}

    elif type(iterable) == list:
        return [filter_by_field_names(a_dict, field_names)
                for a_dict in iterable]


class BonAPI(object):
    base_url = "http://carleton.cafebonappetit.com/cafe"

    cafe_key = u'current_cafe'
    meal_key = u'dayparts'
    entree_key = u'menu_items'
    base_fields = [u'id', u'label']
    cafes = {"east-hall", "burton-hall",
             "sayles-hill-cafe", "weitz-cafe"}

    def __init__(self):
        self.cafe = None
        self.food_choices = None
        self.meals = None

        self.ghost = Ghost(wait_timeout=15,
                           display=False,
                           download_images=False)

    @property
    def data(self):
        data = {self.cafe_key: self.cafe,
                self.entree_key: self.food_choices,
                self.meal_key: self.meals}
        return data

    def get_data(self, cafe, day):

        url = "%s/%s" % (self.base_url, cafe
                         ) if cafe in self.cafes else self.base_url
        url += "/" + day.isoformat()  # ex: '2015-01-01'
        try:
            page, resources = self.ghost.open(url)
            if page.http_status == 200:
                bamco, _ = self.ghost.evaluate("Bamco")
                if bamco:
                    self.filter_data(bamco)
                if self.food_choices is None or len(self.food_choices):
                    print "Bad data, retrying"
                    return self.get_data(cafe, day)
                self.ghost.exit()
                return self.data
        except TimeoutError as t:
            print t
            return self.get_data(cafe, day)

    def filter_data(self, bamco_dict):
        """ Sifts the valuable data from the javascript output."""

        self.cafe = bamco_dict.get(self.cafe_key)
        self._handle_entrees(bamco_dict.get(self.entree_key))
        self._handle_meals(bamco_dict.get(self.meal_key))

    def _handle_entrees(self, entrees):
        if not entrees:
            return entrees

        desc = u'description'
        food_fields = self.base_fields + [desc, u'cor_icon', u'station']

        replacements = (
            (re.compile(r' (\([^G]?G?\))'), ""),
            (re.compile(r'\s+'), " ")
        )

        for food_id in entrees:
            info = filter_by_field_names(entrees[food_id], food_fields)

            description, label = info[desc], info[u'label']
            for regex, new in replacements:
                description = regex.sub(new, description)
                label = regex.sub(new, label)

            info[desc], info[u'label'] = description, label
            entrees[food_id] = info

        self.food_choices = entrees

    def _handle_meals(self, dayparts):
        if not dayparts:
            return dayparts

        stations = u'stations'

        meal_fields = self.base_fields + [stations, u'starttime', u'endtime']
        station_fields = self.base_fields + [u'items']

        meal_data = self._use_labels_as_keys(dayparts)
        for meal_name in meal_data:
            info = filter_by_field_names(meal_data[meal_name], meal_fields)
            meal_stations = self._use_labels_as_keys(info[stations])

            for stat_name in meal_stations:
                stat_info = filter_by_field_names(meal_stations[stat_name],
                                                  station_fields)
                if stat_info.get(u'items', None):
                    items = stat_info[u'items']
                    stat_info[u'items'] = [self.food_choices.pop(eid, eid)
                                           for eid in items
                                           if type(eid) == unicode]
                meal_stations[stat_name] = stat_info

            info[stations] = meal_stations
            meal_data[meal_name] = info

        self.meals = meal_data

    @staticmethod
    def _use_labels_as_keys(collection):
        """ Returns a dict where the keys are the labels of each element."""
        if type(collection) == dict:
            return {all_info.pop(u'label'): all_info
                    for (old_id, all_info) in collection.items()}
        elif type(collection) == list:
            return {all_info.pop(u'label'): all_info
                    for all_info in collection}


def profile(runs=1):
    deltas = []
    for i in range(runs):
        start = datetime.datetime.now()
        bon_api = BonAPI()
        bon_api.get_data("east-hall", datetime.date.today())
        delta = datetime.datetime.now() - start
        print delta
        deltas.append(delta)
    print "Average: ", (sum(deltas, datetime.timedelta())/runs)


if __name__ == '__main__':
    bon_api = BonAPI()
    pprint(bon_api.get_data("east-hall",
                            datetime.date.today()))
