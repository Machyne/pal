#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

import requests

from config import GOOGLE_GEOCODE_KEY as API_KEY

def geocode(location, default=None):
    url = ("https://maps.googleapis.com/maps/api/geocode/json?"
           "address={}&key={}")
    url = url.format(location.replace(' ', '+'), API_KEY)
    r = requests.get(url)
    json = r.json()
    if json['status'] != 'OK':
        return default
    results = json['results']
    if isinstance(results, list):
        results = results[0]
    loc = results['geometry']['location']
    return [loc['lat'], loc['lng']]

if __name__ == '__main__':
    print geocode('Northfield, MN', 'no response')
