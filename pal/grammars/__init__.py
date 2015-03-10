#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from os import path

from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import generate_grammar_features


def get_grammar_for_service(short_name):
    file_name = '{0}_grammar.txt'.format(short_name)
    file_path = path.abspath(path.join(path.dirname(__file__),
                                       'services', file_name))
    grammar = parse_grammar_from_file(file_path)
    make_chomsky_normal_form(grammar)
    grammar_features = generate_grammar_features(grammar)
    return grammar_features
