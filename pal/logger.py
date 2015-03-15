#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

import logging
from logging import Formatter
import re

heuristic_logger = logging.getLogger('Heuristics')
heuristic_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('hill_climb.log')
file_handler.setLevel(logging.DEBUG)
# formatter only supports %s formatting
file_handler.setFormatter(Formatter('%(message)s'))

heuristic_logger.addHandler(file_handler)

class Logger(object):
    LOGGER = logging.getLogger('PAL Engine')
    H_LOGGER = logging.getLogger('Heuristics')

    @classmethod
    def process(cls, params):
        copy = params.copy()
        for k, v in copy['user-data'].iteritems():
            # Redact sensitive information.
            if 'cc-' in k or 'credit' in k or 'cvv' in k:
                copy['user-data'][k] = re.sub('.', '*', v)

        cls.LOGGER.info(copy)

    @classmethod
    def log_heuristic(cls, msg):
        cls.H_LOGGER.info(msg)
