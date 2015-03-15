#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.


class Sanitizer(object):
    _PERMITTED_KEYS = ['result', 'service']

    @classmethod
    def process(cls, params):
        for key in params.keys():
            if key not in cls._PERMITTED_KEYS:
                del params[key]
