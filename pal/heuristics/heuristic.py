#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.
#
# A place to collect utility functions that could be useful across components

from os import path
from collections import OrderedDict


class Heuristic(object):

    def __init__(self, heuristic_name):
        self._variables = OrderedDict()
        self._name = heuristic_name
        self.read_input_file()

    def _get_score(self, word):
        score = self._variables.get(word, 0)
        while isinstance(score, str):
            score = self._variables.get(score, 0)
        return score

    # Returns a heuristic value for a list of keywords
    def run_heuristic(self, keywords):
        kws = keywords + ['BIAS']
        return sum(self._get_score(word) for word in kws)

    def read_input_file(self):
        # read input file into dictionary with keyword as key and
        # heuristic score as value
        fname = self.climbed_file_name
        lines = []
        try:
            with open(fname, 'rb') as input_file:
                lines = input_file.readlines()
        except IOError:
            fname = self.unclimbed_file_name
            with open(fname, 'rb') as input_file:
                lines = input_file.readlines()
        dummy_count = 0
        in_list = False
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('['):
                if in_list:
                    raise SyntaxError(
                        'File "{}", line {}, nested lists not supported'
                        .format(fname, i + 1))
                in_list = True
                dummy_count += 1

            elif line.startswith(']'):
                val = int(line.split(',')[1].strip())
                self._variables['dummy_var_{}'.format(dummy_count)] = val
                in_list = False

            elif in_list:
                key = line.split(',')[0].strip()
                self._variables[key] = 'dummy_var_{}'.format(dummy_count)

            elif ',' in line:
                cur_line = map(str.strip, line.split(','))
                self._variables[cur_line[0]] = int(cur_line[1])

    def write_to_file(self, fname):
        with open(fname, 'w') as file_:
            in_dummy = False
            for k, v in self._variables.iteritems():
                if isinstance(v, int) and not in_dummy:
                    file_.write('{}, {}\n'.format(k, v))
                elif isinstance(v, str):
                    if not in_dummy:
                        file_.write('[\n')
                        in_dummy = True
                    file_.write('    {}\n'.format(k))
                else:
                    file_.write('], {}\n'.format(v))
                    in_dummy = False

    def get_input_list_values(self):
        return filter(lambda x: isinstance(x, int),
                      self._variables.itervalues())

    def _get_keys_from_value(self, val):
        return [k for k, v in self._variables.iteritems() if v == val]

    def _get_key_or_list(self, key):
        """ if the input key is a valid key, return it, else if it is
            invalid (starts with dummy_var_), return all keys that have
            the value of that dummy_var.
        """
        if not key.startswith('dummy_var_'):
            return key
        return self._get_keys_from_value(key)

    def get_input_list_keywords(self):
        items = filter(lambda x: isinstance(x[1], int),
                       self._variables.iteritems())
        keys = map(lambda i: i[0], items)
        return map(self._get_key_or_list, keys)

    @property
    def climbed_file_name(self):
        return path.realpath(
            path.join(
                path.dirname(__file__),
                'hill_climb',
                'climbed_values',
                '{}_climbed_values.txt'.format(self._name)))

    @property
    def unclimbed_file_name(self):
        return path.realpath(
            path.join(
                path.dirname(__file__),
                'values',
                '{}_values.txt'.format(self._name)))

if __name__ == '__main__':
    my_heur = Heuristic('movie')
    print my_heur.get_input_list_keywords()
    my_heur = Heuristic('stalkernet')
    print my_heur.get_input_list_keywords()
