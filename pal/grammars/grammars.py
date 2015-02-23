# GRAMMARS
#
# A grammar must be specified in a .txt file as follows:
#
#   - The first nonterminal is taken to be the start symbol.
#   - Terminals are denoted by double quotes
#   - Allowed operators are:
#       ?   for optional
#       ()  for and
#       []  for or
#   - Non terminals may use spaces but underscores are preferred.
#   - Non terminals must not begin with an underscore.
#   - The star * denotes an arbitrary string production (NOT IMPLEMENTED).
#
# Two kinds of grammar representation are used:
#
#   Form 1: More flexible, used when a grammar file is initally parsed.
#
#   Form 2: The preferred form, requires the grammar to be in CNF.
#
#           In this second form, a grammar is a dict of key-value pairs,
#           k, v, where v is a list of allowed productions of k, and each
#           item in the list is either a string for a terminal production
#           or a 2-tuple for a nonterminal production. The exception is the
#           key '$' whose value is the start symbol, as a string.


import pprint
import re
from collections import defaultdict


def main():
    """ Reads a grammar from a file and converts it to CNF. """
    grammar = parse_grammar_from_file('grammar.txt')
    original_rule_count = count_rules(grammar)
    original_depth = measure_depth(grammar)
    make_chomsky_normal_form(grammar)
    pprint.pprint(grammar)
    print
    print 'Original rule count \t', original_rule_count
    print 'CNF rule count \t\t', count_rules(grammar)
    print 'Original depth \t\t', original_depth
    print 'CNF depth \t\t', measure_depth_cnf(grammar)
    print


def is_terminal(symbol):
    return symbol[0] == '"'


def is_nonterminal(symbol):
    return not is_terminal(symbol)


def split_csv(line):
    """ Given a string of comma separated values, returns a list of
        those values, without whitespace around the items.
    """
    return map(str.strip, line.split(','))


def find_bracketed_group(line):
    """ Returns the start (inclusive) and end (exclusive) indices of the
        first outermost pair of parentheses '()' or brackets '[]'.
    """
    bracket = None
    depth = 0
    for i, c in enumerate(line):
        if c in '([':
            if depth == 0:
                bracket = c
                start = i
            depth += 1
        elif c in ')]':
            depth -= 1
        if depth == 0 and bracket is not None:
            end = i + 1
            assert bracket == '(' and c == ')' or bracket == '[' and c == ']'
            break
    if bracket:
        return start, end
    else:
        return None, None


def find_multiword_string(line):
    """ Returns the start (inclusive) and end (exclusive) indices of the
        first multiword string literal (a string surrounded by double-quotes).
    """
    match = re.search(r'("\w+(?: \w+)+")', line)
    if match:
        return match.start(), match.end()
    else:
        return None, None


def parse_grammar_from_file(filename):
    """ Given the path to a text file describing a grammar, returns a dict
        whose keys include the nonterminals of the gramma, and whose values
        are lists of possible generated sequence, where each sequence is
        represented by a list of terminals (in quotes) and nonterminals.
    """
    grammar = defaultdict(list)
    re_extract_nonterminal = re.compile(r'([\w ]+?):(.*)$')

    def parse_rule(outer_name, line):
        """ Returns a version of the rule without parentheses or brackets,
            by creating new "inner rules" and adding them to the grammar.
            Also, new rules are created to replace multi-word string literals.
        """
        inner_rule_count = [0]

        def next_inner_nonterminal():
            while True:
                inner_nonterminal = ('_{0}_{1}'.format(
                                     inner_rule_count[0], outer_name))
                if inner_nonterminal not in grammar:
                    return inner_nonterminal
                inner_rule_count[0] += 1

        while True:
            start, end = find_multiword_string(line)
            if start is None:
                break
            else:
                string_literal = line[start + 1:end - 1]
                inner_nonterminal = '_' + string_literal.replace(' ', '_')
                if inner_nonterminal not in grammar:
                    inner_rule = [['"{0}"'.format(word)
                                   for word in string_literal.split()
                                   ]]
                    grammar[inner_nonterminal] = inner_rule
                line = line[:start] + inner_nonterminal + line[end:]

        while True:
            start, end = find_bracketed_group(line)
            if start is None:
                break
            else:
                inner_rule = parse_rule(outer_name, line[start + 1:end - 1])
                inner_nonterminal = next_inner_nonterminal()
                if line[start] == '(':
                    grammar[inner_nonterminal] = [split_csv(inner_rule)]
                else:
                    grammar[inner_nonterminal] = [[x] for x in
                                                  split_csv(inner_rule)]
                line = line[:start] + inner_nonterminal + line[end:]

        return line

    start_symbol = None
    with open(filename) as f:
        nonterminal = None
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            if not line:
                nonterminal = None
            elif not nonterminal:
                nonterminal, line = re_extract_nonterminal.match(line).groups()
                if start_symbol is None:
                    start_symbol = nonterminal
                line = line.strip()
                multiline = not line
            if line and nonterminal:
                rule_string = parse_rule(nonterminal, line)
                grammar[nonterminal].append(split_csv(rule_string))
            if nonterminal and not multiline:
                nonterminal = None
    grammar['$'] = [[start_symbol]]
    return dict(grammar)


def remove_question_rules(grammar):
    for key, rules in grammar.iteritems():
        rules_to_scan = rules
        while rules_to_scan:
            new_rules = []
            for rule in rules_to_scan:
                for i in xrange(len(rule)):
                    if rule[i][-1] == '?':
                        rule[i] = rule[i][:-1]
                        new_rule = rule[:i] + rule[i + 1:]
                        grammar[key].append(new_rule)
                        new_rules.append(new_rule)
            rules_to_scan = new_rules


def convert_unit_rules(grammar):
    def is_unit_rule(rule):
        return len(rule) == 1 and not is_terminal(rule[0])
    changed = True
    removed_unit_rules = []
    while changed:
        changed = False
        for key, rules in grammar.iteritems():
            if key == '$':
                continue
            non_unit_rules = []
            for rule in rules:
                if is_unit_rule(rule):
                    a, b = key, rule[0]
                    removed_unit_rules.append((a, b))
                    changed = True

                    # Make new rules
                    b_rules = grammar[b]
                    for b_rule in b_rules:
                        if not (is_unit_rule(b_rule) and
                                (a, b_rule[0]) in removed_unit_rules):
                            grammar[a].append(b_rule)
                else:
                    non_unit_rules.append(rule)
            grammar[key] = non_unit_rules


def remove_unused_rules(grammar):
    keys_to_delete = [None]
    while keys_to_delete:
        keys_to_delete = []
        grammar_repr = repr(grammar)
        for key in grammar:
            if grammar_repr.count(key) == 1 and key != "$":
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del grammar[key]


def convert_long_rules(grammar):
    subkey_counts = defaultdict(int)

    def next_subkey(key):
        while True:
            subkey = ('_{0}_{1}'.format(subkey_counts[key], key))
            if subkey not in grammar:
                return subkey
            subkey_counts[key] += 1

    for key, rules in grammar.items():  # Must be items not iteritems
        for i in xrange(len(rules)):
            rule = rules[i]
            if len(rule) > 2:
                subkey = next_subkey(key)
                rules[i] = [rule[0], subkey]
                rule = rule[1:]
                while len(rule) > 2:
                    oldkey = subkey
                    grammar[oldkey] = []
                    subkey = next_subkey(key)
                    grammar[oldkey] = [[rule[0], subkey]]
                    rule = rule[1:]
                grammar[subkey] = [rule]


def convert_terminal_productions(grammar):
    for key, rules in grammar.items():  # Must be items not iteritems
        for rule in rules:
            if len(rule) == 2:
                for i in xrange(len(rule)):
                    if is_terminal(rule[i]):
                        terminal = rule[i]
                        nonterminal = '_' + terminal[1:-1]
                        rule[i] = nonterminal
                        grammar[nonterminal] = [[terminal]]


def convert_data_types(grammar):
    for key, rules in grammar.items():  # Must be items not iteritems
        if key == '$':
            continue
        for i in xrange(len(rules)):
            rule = rules[i]
            if is_terminal(rule[0]):
                rules[i] = rule[0][1:-1]
            else:
                rules[i] = tuple(rule)
    grammar['$'] = grammar['$'][0][0]


def make_chomsky_normal_form(grammar):
    remove_question_rules(grammar)
    # convert_unit_rules(grammar)
    remove_unused_rules(grammar)
    convert_long_rules(grammar)
    convert_terminal_productions(grammar)
    convert_data_types(grammar)


def count_rules(grammar):
    return sum(len(rules) for key, rules in grammar.iteritems() if key != '$')


def measure_depth(grammar):
    """ Measures the max number of steps from a start symbol to a terminal,
        given a grammar that is represented in the first form.

        I'm honestly not sure what happens when you have self-referential
        productions rules.
    """
    key_depths = {}

    def measure_depth_of_key(key):
        if key in key_depths:
            return key_depths[key]
        rules = grammar[key]
        depth = 0
        for rule in rules:
            rule_depths = map(measure_depth_of_key,
                              map(
                                  lambda el: el[:-1] if el[-1] == '?' else el,
                                  filter(is_nonterminal, rule))
                              )
            rule_depth = rule_depths and max(rule_depths) or 0
            depth = max(depth, 1 + rule_depth)
        key_depths[key] = depth
        return depth

    return measure_depth_of_key('$') - 1


def measure_depth_cnf(cnf_grammar):
    """ Measures the max number of steps from a start symbol to a terminal,
        given a grammar that is represented in the second (CNF) form.

        Again I don't know what happens when you have self-referential
        productions rules.
    """
    key_depths = {}

    def is_nonterminal_rule(rule_rhs):
        return isinstance(rule_rhs, tuple)

    def measure_depth_of_key(key):
        if key in key_depths:
            return key_depths[key]
        rules = cnf_grammar[key]
        depth = 1
        for rule in filter(is_nonterminal_rule, rules):
            rule_depths = map(measure_depth_of_key, rule)
            depth = max(depth, 1 + max(rule_depths))
        key_depths[key] = depth
        return depth

    return measure_depth_of_key(cnf_grammar['$'])


if __name__ == '__main__':
    main()
