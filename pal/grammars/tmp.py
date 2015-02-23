import pprint
from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import parse, generate_grammar_features, extract, search

string = 'how much for a medium pizza with pineapple but no cheese sauce or mushrooms'

grammar = parse_grammar_from_file('pal/grammars/services/dominos_grammar.txt')
make_chomsky_normal_form(grammar)
grammar_features = generate_grammar_features(grammar)
parse_tree = parse(string, grammar_features)
pprint.pprint(parse_tree)


print 'NOT'
for x in search(parse_tree, 'negation_phrase topping_item'):
    print extract(x[0], x)  # flatten


print '\nWITH'
for x in set(search(parse_tree, 'topping_item')).difference(set(search(parse_tree, 'negation_phrase topping_item'))):
    print extract(x[0], x)  # flatten
