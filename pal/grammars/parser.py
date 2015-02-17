import pprint
import re
import sys
from collections import defaultdict

from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file


def main():
    grammar = parse_grammar_from_file(sys.argv[1])
    make_chomsky_normal_form(grammar)
    grammar_features = generate_grammar_features(grammar)
    pprint.pprint(grammar)
    while True:
        string = raw_input().strip().lower()
        if not string:
            continue
        if string[-1] in ['.', '?', '!']:
            string = string[:-1]
        print parse(string, grammar_features)


def generate_grammar_features(grammar):
    key_list = sorted([key for key in grammar.iterkeys() if not key == '$'])
    unit_rules = []
    non_unit_rules = []
    for i, key in enumerate(key_list):
        rules = grammar[key]
        for rule in rules:
            if isinstance(rule, str):
                unit_rules.append((i, rule))
            elif isinstance(rule, tuple):
                b = key_list.index(rule[0])
                c = key_list.index(rule[1])
                non_unit_rules.append((i, b, c))
    lexicon = [rule[1] for rule in unit_rules]
    start_key_index = key_list.index(grammar['$'])
    return unit_rules, non_unit_rules, lexicon, start_key_index


def parse(string, grammar_features):
    def wild_card(word):
        try:
            int(word, 10)
            return '#'
        except ValueError:
            return '*'
    lexicon = grammar_features[2]
    words = [word if word in lexicon else wild_card(word)
             for word in string.split()]
    string = ' '.join(words)
    string = re.sub(r'(\*|#)( (\*|#))+', '*', string)
    return cyk(string, *grammar_features)


def cyk(string, unit_rules, non_unit_rules, lexicon, start_key_index):
    """ CYK algorithm. Returns True if the string is parsed by the grammar. """
    words = string.split()
    words_count = len(words)
    p = defaultdict(bool)
    for i in xrange(words_count):
        for rule in unit_rules:
            j, rhs = rule
            if rhs == words[i]:
                p[(0, i, j)] = True
    for i in xrange(1, words_count):
        for j in xrange(words_count - i):
            for k in xrange(i):
                for rule in non_unit_rules:
                    a, b, c = rule
                    if p[(k, j, b)] and p[(i - k - 1, j + k + 1, c)]:
                        p[(i, j, a)] = True
    return p[(words_count - 1, 0, start_key_index)]


if __name__ == '__main__':
    main()
