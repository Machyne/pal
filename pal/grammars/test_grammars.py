from collections import defaultdict
from os import path

from pal.grammars import get_grammar_for_service
from pal.grammars.parser import parse


_GRAMMARS_DIR = path.abspath(path.join(path.dirname(__file__),
                                       'services'))
_EXAMPLES_FILE = path.abspath(path.join(path.dirname(__file__),
                                        '..', 'test', 'examples.txt'))


def main():
    test_grammar('movie')


def test_grammar(service_name):
    print('Testing grammar for service \'{0}\'...'.format(service_name))
    grammar = get_grammar_for_service(service_name)
    all_examples = load_examples_from_file(_EXAMPLES_FILE)
    ex_total = 0
    counter_ex_total = 0
    hits = 0
    misses = 0
    for key, examples in all_examples.iteritems():
        if key == service_name:
            ex_total += len(examples)
            for example in examples:
                if parse(example, grammar):
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


def load_examples_from_file(examples_file):
    with open(examples_file) as f:
        examples = defaultdict(list)
        cur_name = None
        for line in f:
            line = line.strip()
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