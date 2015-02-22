from pal.grammars.grammars import is_terminal
from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file


def main():
    """ Generates the language of a grammar. """
    grammar = parse_grammar_from_file('pal/grammars/services/movie_grammar.txt')
    make_chomsky_normal_form(grammar)
    try:
        language = generate_language_cnf(grammar)
        language.sort()
        for phrase in language:
            print phrase
        print 'Size of language:', len(language)
    except KeyError as e:
        print 'Error: No rule for symbol \'{0}\''.format(e.args[0])


# A set of non terminals that should not be expanded when generating the
# full language of a grammar, so that we can get a reasonable summary
# of the language.
_NO_EXPAND = set(['feature', 'include', 'star', 'direct', 'make', 'write',
                  'movie_word', 'person_word', 'aux'
                  ])


def generate_language_cnf(cnf_grammar):
    """ Returns the language of a grammar in form 2 (CNF). """
    key_productions = {key: [[key]] for key in _NO_EXPAND}

    def is_terminal_rule(rule_rhs):
        return isinstance(rule_rhs, str)

    def is_nonterminal_rule(rule_rhs):
        return isinstance(rule_rhs, tuple)

    def productions_of_key(key):
        if key in key_productions:
            return key_productions[key]
        rules = cnf_grammar[key]
        productions = [[word] for word in filter(is_terminal_rule, rules)]
        for rule in filter(is_nonterminal_rule, rules):
            left = productions_of_key(rule[0])
            right = productions_of_key(rule[1])
            for l in left:
                productions += [l + r for r in right]
        key_productions[key] = productions
        return productions

    productions = productions_of_key(cnf_grammar['$'])
    language = [' '.join(production) for production in productions]
    return language


def generate_language(grammar, start_symbol):
    """ Returns the language of a grammar in form 1, given a start symbol.

        WARNING: This doesn't seem to work. About half the phrases are missing.
    """
    language = []

    class DFSNode(object):
        def __init__(self, symbol, parent=None, remainder=[]):
            self.symbol = symbol
            self.parent = parent
            self.remainder = remainder

        def __str__(self):
            return '{0} {1}'.format(self.symbol, self.remainder)

    def reconstruct_path(node):
        terminals = []
        while node.parent:
            if is_terminal(node.symbol):
                terminals.append(node.symbol[1:-1])
            elif node.symbol in _NO_EXPAND:
                terminals.append(node.symbol)
            node = node.parent
        terminals.reverse()
        return terminals

    def expand(node):
        if node.symbol[-1] == "?":
            if node.remainder:
                rule = node.remainder
                extra_child_node = DFSNode(rule[0], node.parent, rule[1:])
                expand(extra_child_node)
            else:
                extra_path = reconstruct_path(node.parent)
                extra_phrase = ' '.join(extra_path)
                language.append(extra_phrase)
            node.symbol = node.symbol[:-1]
        if is_terminal(node.symbol) or node.symbol in _NO_EXPAND:
            if node.remainder:
                rule = node.remainder
                child_node = DFSNode(rule[0], node, rule[1:])
                expand(child_node)
            else:
                path = reconstruct_path(node)
                phrase = ' '.join(path)
                language.append(phrase)
        else:
            children_nodes = [DFSNode(rule[0], node, rule[1:] + node.remainder)
                              for rule in grammar[node.symbol]]
            for child_node in children_nodes:
                expand(child_node)

    root = DFSNode(start_symbol)
    expand(root)
    return language


if __name__ == '__main__':
    main()
