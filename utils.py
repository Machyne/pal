#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

#
# A place to collect utility functions that could be useful across components

from datetime import date
from datetime import timedelta

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday']


def infer_date(date_word):
    """ Given a day string, return a corresponding python date object """
    date_word = date_word.lower()
    current_date = date.today()
    if date_word == "today":
        return current_date
    if date_word == "tomorrow":
        tomorrow = current_date + timedelta(days=1)
        return tomorrow
    if date_word in weekdays:
        desired_day = weekdays.index(date_word)
        current_day = current_date.weekday()
        days_in_future = (desired_day - current_day) % 7
        return current_date + timedelta(days=days_in_future)


def filter_dict_by_keys(dict_, field_names):
    """ Returns a copy of `dict_` with only the fields in `field_names`"""
    return {key: value for (key, value) in dict_.items()
            if key in field_names}
