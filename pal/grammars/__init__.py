from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import generate_grammar_features


_GRAMMARS_DIR = 'pal/grammars/services'


def get_grammar_for_service(short_name):
    grammar_file = '{0}/{1}_grammar.txt'.format(_GRAMMARS_DIR, short_name)
    grammar = parse_grammar_from_file(grammar_file)
    make_chomsky_normal_form(grammar)
    grammar_features = generate_grammar_features(grammar)
    return grammar_features
