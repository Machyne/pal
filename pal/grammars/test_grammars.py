from pprint import pprint
from collections import defaultdict
from os import path

from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parse
from pal.test import parse_examples


_GRAMMARS_DIR = path.abspath(path.join(path.dirname(__file__),
                                       'services'))


def main():
    test_grammar('movie')
    test_grammar('dominos')


def test_grammar(service_name):
    print('Testing grammar for service \'{0}\'...'.format(service_name))
    try:
        grammar = get_grammar_for_service(service_name)
    except ValueError as e:
        print 'Error: {}'.format(e.args[0])
        return
    all_examples = parse_examples()
    ex_total = 0
    counter_ex_total = 0
    hits = 0
    misses = 0
    for key, examples in all_examples.iteritems():
        if key == service_name:
            ex_total += len(examples)
            for example in examples:
                parse_tree = parse(example, grammar)
                if parse_tree:
                    # pprint(parse_tree)
                    # print example
                    # print '\torder:', not extract(parse_tree, 'price_query')
                    # print '\tnumber:', extract(parse_tree, 'number') or 'one'
                    # print '\tcrust_type:', extract(parse_tree, 'crust_type', True)
                    # print '\tcrust_size:', extract(parse_tree, 'crust_size', True)
                    hits += 1
                else:
                    print '>', example
        else:
            counter_ex_total += len(examples)
            for counterexample in examples:
                if parse(counterexample, grammar):
                    misses += 1
                    print 'X', counterexample
    print('Success:\t\t{0}/{1}'.format(hits, ex_total))
    print('False Positives:\t{0}/{1}'.format(misses, counter_ex_total))


if __name__ == '__main__':
    main()
