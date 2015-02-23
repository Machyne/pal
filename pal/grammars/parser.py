import pprint
import re
import sys

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
    unit_rules = []
    pair_rules = []
    for i, key in enumerate(key_list):
        rules = grammar[key]
        for rule in rules:
            if isinstance(rule, str):
                terminal_rules.append((i, rule))
            elif isinstance(rule, tuple):
                b = key_list.index(rule[0])
                if len(rule) == 1:
                    unit_rules.append((i, b))
                if len(rule) == 2:
                    c = key_list.index(rule[1])
                    pair_rules.append((i, b, c))
    lexicon = [rule[1] for rule in terminal_rules]
    start_key = key_list.index(grammar['$'])
    return key_list, terminal_rules, unit_rules, pair_rules, lexicon, start_key


def preprocess(string, grammar_features):
    """ Normalize string, convert numbers and unknown words to wild cards. """
    string = re.sub('(.*)[\.\?!]$', '\\1', string.strip().lower())

    def wild_card(word):
        try:
            int(word, 10)
            return '#'
        except ValueError:
            return '*'
    lexicon = grammar_features[4]
    words = [word if word in lexicon else wild_card(word)
             for word in string.split()]
    string = ' '.join(words)
    # string = re.sub(r'(\*|#)( (\*|#))+', '*', string)
    return string


def parse(string, grammar_features):
    """ Returns a parse if the string is parsed by the grammar else [].

        Note: Expects a lowercase string without ending punctuation.
    """
    original_words = string.split()
    string = preprocess(string, grammar_features)
    tokens = string.split()
    parse_tree = cyk(tokens, original_words, grammar_features)
    return clean_tree(parse_tree)


def clean_tree(parse_tree):
    if not isinstance(parse_tree, tuple):
        return parse_tree
    root, subtree_list = parse_tree
    new_subtree_list = ()
    for subtree in subtree_list:
        subtree = clean_tree(subtree)
        root2 = subtree[0]
        if root2[0] == '_':
            for subtree_list2 in subtree[1:]:
                new_subtree_list += subtree_list2
        else:
            new_subtree_list += (subtree,)
    return root, new_subtree_list


def cyk(tokens, original_words, grammar_features):
    """ Runs a modified form of the CYK algorithm which allows for
        unit rules in the grammar.
    """
    (key_list, terminal_rules, unit_rules, pair_rules,
        lexicon, start_key) = grammar_features
    tokens_count = len(tokens)
    p = {}
    for i in xrange(tokens_count):
        for rule in terminal_rules:
            j, rhs = rule
            if rhs == tokens[i]:
                p[(0, i, j)] = (key_list[j], (original_words[i],))
        changed = True
        while changed:
            changed = False
            for rule in unit_rules:
                a, b = rule
                if (0, i, b) in p and (0, i, a) not in p:
                    p[(0, i, a)] = (key_list[a], (p[(0, i, b)],))
                    changed = True
    for i in xrange(1, tokens_count):
        for j in xrange(tokens_count - i):
            for k in xrange(i):
                for rule in pair_rules:
                    a, b, c = rule
                    if (k, j, b) in p and (i - k - 1, j + k + 1, c) in p:
                        p[(i, j, a)] = (key_list[a], (p[(k, j, b)],
                                        p[(i - k - 1, j + k + 1, c)]))
            changed = True
            while changed:
                changed = False
                for rule in unit_rules:
                    a, b = rule
                    if (i, j, b) in p and (i, j, a) not in p:
                        p[(i, j, a)] = (key_list[a], (p[(i, j, b)],))
                        changed = True
    if (tokens_count - 1, 0, start_key) in p:
        return p[(tokens_count - 1, 0, start_key)]
    else:
        return False


def extract(symbol, parse_tree, get_nonterminals=False):
    """ Returns the substring that was expanded from the given symbol in
        the parse indicated by the parse tree.
    """
    def flatten(parse_tree):
        if not isinstance(parse_tree, tuple):
            return [parse_tree]
        root, subtree_list = parse_tree
        return [item for subtree in subtree_list for item in flatten(subtree)]

    if not isinstance(parse_tree, tuple):
        return False
    root, subtree_list = parse_tree
    if root == symbol:
        words = flatten(parse_tree)
        return ' '.join(words)
    else:
        for subtree in subtree_list:
            subresult = extract(symbol, subtree)
            if subresult:
                return subresult
        return ''


def search(node, selector):
    if isinstance(node, tuple):
        if ' ' in selector:
            l, _, r = selector.partition(' ')
            for found1 in search(node, l):
                for found2 in search(found1, r):
                    yield found2
        else:
            if node[0] == selector:
                yield node
            else:
                for child in node[1]:
                    for found in search(child, selector):
                        yield found


def parent(tree, node):
    """ returns false if node is not in the tree """
    if not isinstance(tree, tuple):
        return False
    subtrees = tree[1]
    if node in subtrees:
        return tree
    for subtree in subtrees:
        p = parent(subtree, node)
        if p:
            return p
    return False


if __name__ == '__main__':
    main()
