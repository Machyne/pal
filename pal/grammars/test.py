#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.
#
# Tests that the grammars modules do what they're supposed to.

from pal.grammars.generator import generate_language
from pal.grammars.generator import generate_language_cnf
from pal.grammars.grammars import count_rules
from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import generate_grammar_features
from pal.grammars.parser import parse


_GRAMMAR_FILE = 'pal/grammars/test_grammar.txt'
_LANGUAGE_FILE = 'pal/grammars/test_language.txt'


def main():
    ''' Reads a grammar from a file. Checks that it generates the language.
        Converts the grammar to CNF. Checks that the grammar is in CNF, and
        that it still generates the language.
    '''
    print('Loading grammar from file "{0}"...'.format(_GRAMMAR_FILE))
    grammar = parse_grammar_from_file(_GRAMMAR_FILE)
    with open(_LANGUAGE_FILE) as f:
        language = filter(lambda x: not not x,
                          map(lambda x: x.strip(), f.read().split('\n')))
    check_grammar(grammar, language, cnf=False)
    print('Converting grammar to CNF...')
    make_chomsky_normal_form(grammar)
    check_grammar(grammar, language, cnf=True)
    check_cnf(grammar)
    print('Testing the CYK parser...')
    test_parser(language, [], grammar)


def test_parser(in_language, not_in_language, grammar):
    grammar_features = generate_grammar_features(grammar)
    try:
        for string in in_language:
            assert parse(string, grammar_features)
        for string in not_in_language:
            assert not parse(string, grammar_features)
    except AssertionError as e:
        e.args += (string,)
        raise
    print('SUCCESS')


def check_grammar(grammar, language, cnf):
    ''' Throws an error if the language generated by the grammar is not
        equal to the language enumerated in the file _LANGUAGE_FILE.
    '''
    rule_count = count_rules(grammar)
    print('Grammar contains {0} rules.'.format(rule_count))
    print('Generating language...')
    try:
        if cnf:
            generated_language = generate_language_cnf(grammar)
        else:
            generated_language = generate_language(grammar, '$')
    except KeyError as e:
        print('Error: No rule for symbol \'{0}\''.format(e.args[0]))
        raise
    generated_language.sort()
    print('Verifying language...')
    assert len(language) == len(generated_language)
    for i in xrange(len(language)):
        try:
            assert language[i] == generated_language[i]
        except AssertionError as e:
            e.args += (language[i],)
            raise
    print('SUCCESS')


def check_cnf(grammar):
    ''' Throws an error if the grammar is not in form 2 (CNF).
    '''
    try:
        print('Verifying CNF...')
        for key, rules in grammar.iteritems():
            if key == '$':
                assert isinstance(rules, str)
                continue
            assert isinstance(rules, list)
            for rule in rules:
                assert isinstance(rule, (str, tuple))
                if isinstance(rule, tuple):
                    assert len(rule) == 2
                    assert rule[0] in grammar
                    assert rule[1] in grammar
    except AssertionError as e:
        e.args += (rule,)
        raise
    print('SUCCESS')


if __name__ == '__main__':
    main()
