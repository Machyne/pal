import sys
from os import path

from pal.heuristics.heuristic import Heuristic
from pal.nlp.keyword_finder import find_keywords
from pal.nlp.standard_nlp import StandardNLP
from pal.services import get_all_service_names
from pal.test import parse_examples

STEPS_BETWEEN_WRITES = 10 # The interval between data writes
THRESHOLD = 15


def get_confs_kws(query, services):
    params = {'query': query}
    StandardNLP.process(params)
    keywords = find_keywords(params['features']['tokens'])
    confidences = {}
    for name, heuristic in services.iteritems():
        confidences[name] = heuristic.run_heuristic(keywords)
    return confidences, keywords

# Returns the set of services to climb on. Otherwise, an empty set
def climbing(examples, services):
    to_be_climbed = set()
    for service, queries in examples.iteritems():
        current = services[service]
        for query in queries:
            confidences, keywords = get_confs_kws(query, services)
            chosen_name = max(confidences.keys(), key=confidences.get)
            conf = confidences[chosen_name]
            if chosen_name != service and conf >= THRESHOLD:
                # Here the query was misclassified
                chosen = services[chosen_name]
                for kw in keywords:
                    if kw in chosen._variables:
                        # traverse through dummies
                        while isinstance(chosen._variables[kw], str):
                            kw = chosen._variables[kw]
                        chosen._variables[kw] -= 1
                    if kw in current._variables:
                        # traverse through dummies
                        while isinstance(current._variables[kw], str):
                            kw = current._variables[kw]
                        current._variables[kw] += 1

                print '"{}"'.format(query)
                print 'was supposed to be in {}'.format(service)
                print 'was in {}'.format(chosen_name)
                print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                to_be_climbed.add(chosen_name)
                to_be_climbed.add(service)

    return to_be_climbed


def main():
    examples = parse_examples()
    services = {s: Heuristic(s) for s in get_all_service_names()}

    services_to_step = climbing(examples, services)

    counter = 0
    while len(services_to_step):
        counter += 1
        sys.stdout.flush()
        services_to_step = climbing(examples, services)

        # Write to file after so many steps, that way we don't lose
        # progress if we end early.
        if counter == STEPS_BETWEEN_WRITES or not len(services_to_step):
            counter = 0
            for name, heuristic in services.iteritems():
                fname = path.realpath(
                    path.join(
                        path.dirname(__file__),
                        'climbed_values',
                        name + '_climbed_values.txt'))
                heuristic.write_to_file(fname)

    print "Success! You did it! Hills have been climbed!"


if __name__ == '__main__':
    main()
