#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

import pprint
from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import parse, generate_grammar_features, extract, search, parent

string = 'how much for two medium thin pizza with extra pineapple but no cheese sauce or mushrooms'

grammar = parse_grammar_from_file('pal/grammars/services/dominos_grammar.txt')
make_chomsky_normal_form(grammar)
grammar_features = generate_grammar_features(grammar)
parse_tree = parse(string, grammar_features)
pprint.pprint(parse_tree)


print 'NOT'
for x in search(parse_tree, 'negation_phrase topping_item'):
    print extract(x, x[0])  # flatten
    print parent(parse_tree, x)[0]


print '\nWITH'
for x in set(search(parse_tree, 'topping_item')).difference(set(search(parse_tree, 'negation_phrase topping_item'))):
    print extract(x, x[0])  # flatten
    print parent(parse_tree, x)[0]
