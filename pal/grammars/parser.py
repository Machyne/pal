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
        parse_tree = parse(string, grammar_features)
        pprint.pprint(parse_tree)
        if parse_tree:
            print 'Extract key:',
            symbol = raw_input().strip().lower()
            print extract(symbol, parse_tree)


def generate_grammar_features(grammar):
    key_list = sorted([key for key in grammar.iterkeys() if not key == '$'])
    terminal_rules = []
    non_terminal_rules = []
    for i, key in enumerate(key_list):
        rules = grammar[key]
        for rule in rules:
            if isinstance(rule, str):
                terminal_rules.append((i, rule))
            elif isinstance(rule, tuple):
                b = key_list.index(rule[0])
                if len(rule) == 1:
                    non_terminal_rules.append((i, b))
                if len(rule) == 2:
                    c = key_list.index(rule[1])
                    non_terminal_rules.append((i, b, c))
    lexicon = [rule[1] for rule in terminal_rules]
    start_key = key_list.index(grammar['$'])
    return key_list, terminal_rules, non_terminal_rules, lexicon, start_key


def preprocess(string, grammar_features):
    """ Normalize string, convert numbers and unknown words to wild cards. """
    string = re.sub('(.*)[\.\?!]$', '\\1', string.strip().lower())

    def wild_card(word):
        try:
            int(word, 10)
            return '#'
        except ValueError:
            return '*'
    lexicon = grammar_features[3]
    words = [word if word in lexicon else wild_card(word)
             for word in string.split()]
    string = ' '.join(words)
    # string = re.sub(r'(\*|#)( (\*|#))+', '*', string)
    return string


def parse(string, grammar_features):
    """ Returns a parse if the string is parsed by the grammar else [].

        Note: Expects a lowercase string without ending punctuation.
    """
    (key_list, terminal_rules, non_terminal_rules,
        lexicon, start_key) = grammar_features
    original_words = string.split()
    string = preprocess(string, grammar_features)
    words = string.split()
    words_count = len(words)
    p = defaultdict(list)
    for i in xrange(words_count):
        for rule in terminal_rules:
            j, rhs = rule
            if rhs == words[i]:
                p[(0, i, j)] = [key_list[j], original_words[i]]
        changed = 1
        while changed:
            changed = 0
            for rule in non_terminal_rules:
                if len(rule) == 2:
                    a, b = rule
                    if p[(0, i, b)] and not p[(0, i, a)]:
                        p[(0, i, a)] = [key_list[a], (p[(0, i, b)],)]
                        changed += 1

    for i in xrange(1, words_count):
        for j in xrange(words_count - i):
            for k in xrange(i):
                for rule in non_terminal_rules:
                    if len(rule) == 3:
                        a, b, c = rule
                        if p[(k, j, b)] and p[(i - k - 1, j + k + 1, c)]:
                            p[(i, j, a)] = [key_list[a], (p[(k, j, b)],
                                            p[(i - k - 1, j + k + 1, c)])]
            changed = 1
            while changed:
                changed = 0
                for rule in non_terminal_rules:
                    if len(rule) == 2:
                        a, b = rule
                        if p[(i, j, b)] and not p[(i, j, a)]:
                            p[(i, j, a)] = [key_list[a], (p[(0, i, b)],)]
                            changed += 1
    return p[(words_count - 1, 0, start_key)]


def extract(symbol, parse_tree):
    """ Returns the substring that was expanded from the given symbol in
        the parse indicated by the parse tree.
    """
    def flatten(parse_tree):
        key, value = parse_tree
        if isinstance(value, tuple):
            left, right = value
            return flatten(left) + flatten(right)
        else:
            return [value]

    key, value = parse_tree
    if key == symbol:
        words = flatten(parse_tree)
        return ' '.join(words)
    else:
        if isinstance(value, tuple):
            left, right = value
            return extract(symbol, left) or extract(symbol, right) or ''
        return ''


if __name__ == '__main__':
    main()
