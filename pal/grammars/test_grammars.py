import re
from collections import defaultdict

from pal.grammars.grammars import make_chomsky_normal_form
from pal.grammars.grammars import parse_grammar_from_file
from pal.grammars.parser import generate_grammar_features
from pal.grammars.parser import parse


_GRAMMARS_DIR = 'pal/grammars/services'
_EXAMPLES_FILE = 'test/examples.txt'


def main():
    test_grammar('movie')


def test_grammar(service_name):
    print('Testing grammar for service \'{0}\'...'.format(service_name))
    grammar_file = '{0}/{1}_grammar.txt'.format(_GRAMMARS_DIR, service_name)
    grammar = parse_grammar_from_file(grammar_file)
    make_chomsky_normal_form(grammar)
    grammar_features = generate_grammar_features(grammar)
    all_examples = load_examples_from_file(_EXAMPLES_FILE)
    ex_total = 0
    counter_ex_total = 0
    hits = 0
    misses = 0
    for key, examples in all_examples.iteritems():
        if key == service_name:
            ex_total += len(examples)
            for example in examples:
                if parse(example, grammar_features):
                    hits += 1
                else:
                    print '>', example
        else:
            counter_ex_total += len(examples)
            for counterexample in examples:
                if parse(counterexample, grammar_features):
                    misses += 1
                    print 'X', counterexample
    print('Success:\t\t{0}/{1}'.format(hits, ex_total))
    print('False Positives:\t{0}/{1}'.format(misses, counter_ex_total))


def load_examples_from_file(examples_file):
    with open(examples_file) as f:
        examples = defaultdict(list)
        cur_name = None
        for raw_line in f:
            line = re.sub('(.*)[\.\?!]$', '\\1', raw_line.strip().lower())
            if cur_name is None:
                if line:
                    cur_name = line
            else:
                if line:
                    examples[cur_name].append(line)
                else:
                    cur_name = None
    return examples


if __name__ == '__main__':
    main()
