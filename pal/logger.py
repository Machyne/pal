#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

import logging
import re


class Logger(object):
    LOGGER = logging.getLogger('PAL Engine')

    @classmethod
    def process(cls, params):
        copy = params.copy()
        for k, v in copy['user-data'].iteritems():
            # Redact sensitive information.
            if 'cc-' in k or 'credit' in k or 'cvv' in k:
                copy['user-data'][k] = re.sub('.', '*', v)

        cls.LOGGER.info(copy)
