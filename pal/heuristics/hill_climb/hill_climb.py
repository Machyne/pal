import random
import sys
from os import path

from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor


random.seed(1337 - 1453) #Totally not a reference to Quinn's comps...

STEPS_BETWEEN_WRITES = 10 # The interval between data writes

#QUERIES_ARE_GOOD = False # This is protection against bad test queries


class service_data (object):
    # Each service maintains a list of its values and associated metadata
    def __init__(self, name):
        self.name = name
        self.values = dict()

    def add_value(self, word, mag):
        self.values[word] = [mag, 0]
                            # [Magnitude, Direction]

    def _get_score(self, word):
        score = self.values.get(word, 0)
        if score != 0:
            score = score[0]
        while isinstance(score, str):
            score = self.values.get(score, 0)
            if score != 0:
                score = score[0]
        return score

    def run_heuristic(self, query_keywords):
        sum = 0
        for word in query_keywords:
            sum += self._get_score(word)
        return sum

class service_holder (object):
    # Holds a dictionary representing the values file and hillclimb
    # direction as the value and the name of the service as the key

    def __init__(self):
        self.services = dict()
        # This is protection against bad test queries
        self.queries_are_good = False

    def add_service(self, service):
        if not service in self.services:
            self.services[service] = self._generate_service_values(service)

    # Returns the dictionary associated with the service
    def get_service(self, service):
        self.add_service(service)
        return self.services[service]

    # Returns a service_data object for service
    def _generate_service_values(self, service):
        # read input file into new dictionary with keyword as key and
        # heuristic score as value

        data = service_data(service)
        file_ = path.realpath(
            path.join(
                path.dirname(path.dirname(__file__)),
                'values',
                service + '_values.txt'))
        lines = []

        input_file = open(file_, 'rb')
        lines = input_file.readlines()

        dummy_count = 0
        in_list = False

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('['):
                if in_list:
                    raise SyntaxError(
                        'File "{}", line {}, nested lists not supported'
                        .format(file_, i + 1))
                in_list = True
                dummy_count += 1

            elif line.startswith(']'):
                val = int(line.split(',')[1].strip())
                data.add_value('dummy_var_{}'.format(dummy_count), val)
                in_list = False

            elif in_list:
                key = line.split(',')[0].strip()
                data.add_value(key, 'dummy_var_{}'.format(dummy_count))

            elif ',' in line:
                cur_line = map(str.strip, line.split(','))
                data.add_value(cur_line[0], int(cur_line[1]))

        return data


# Returns the set of services to climb on. Otherwise, an empty set
def climbing(examples, my_service_holder):
    to_be_climbed = set()
    for service, queries in examples.iteritems():
        cur_service = my_service_holder.get_service(service)
        for query in queries:
            params = {
            'query': query,
            'client': "web"
            }
            StandardNLP.process(params)
            FeatureExtractor.process(params)
            ghetto_classifier(params, my_service_holder)
            if params['service'] != service:
                # This is the key piece of new code.
                # Note that if the query isn't sorted into anything,
                # we currently don't want to futz with it.
                # That leads to bad queries causing climbing...
                # and nobody wants that.
                if params['service'] != 'Unsorted':
                    set_steps(params['features']['keywords'], params['service'],
                                                  my_service_holder, -1)
                    set_steps(params['features']['keywords'], service,
                                                  my_service_holder, 1)

                    print query
                    print "was supposed to be in", service
                    print "was in", params['service']
                    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                    to_be_climbed.add(params['service'])
                    to_be_climbed.add(service)
                    # We are preserving to_be_climbed,
                    # because it is good for efficiency

    return to_be_climbed

# Sets the queries that should be stepped on.
def set_steps(words, service, my_service_holder, direction):
    service_to_step = my_service_holder.get_service(service)
    for word in words:
        if word in service_to_step.values:
            # Handle those damn dummy variables
            if type(service_to_step.values[word][0]) is str:
                placeholder = service_to_step.values[word][0]
                if service_to_step.values[placeholder][1] != direction:
                    service_to_step.values[placeholder][1] += direction

            elif service_to_step.values[word][1] != direction:
                service_to_step.values[word][1] += direction
                # Direction is set to -1 for the query whose values
                # should be decreased, and 1 for the query whose
                # values should be increased. This also makes sure
                # that all steps are always small

            if direction == 1:
                my_service_holder.queries_are_good = True
                # If at least some keywords are getting hit
                # in the service the query should be sorted into,
                # then we know we don't only have dud queries...
                # ...this round.

# Steps the service.
# This has been significantly cut down. Deal with it.
def service_stepper(service, my_service_holder):
    data = my_service_holder.get_service(service)

    for key, value in data.values.iteritems():
        if type(value[0]) is str and value[0].startswith('dummy_var_'):
            #don't climb on dummy variables ever
            pass
        else:
            new_magnitude = (data.values[key][0] + data.values[key][1])
                        #  magnitude + direction
        # We were all sneaky-like, and set the directions manually
        # We will then reset them back to 0.
            data.values[key] = [new_magnitude, 0]

# Blatently "borrowed" from Alex's test code
# Reads in the example query file and returns a dictionary with service
# names as keys and a list of queries as values.
def parse_examples():
    file_path = path.realpath(path.join(path.dirname(__file__),
                                        "examples.txt"))
    examples = {}

    with open(file_path) as ex_file:
        service = ex_file.next().strip()
        queries = []
        for line in ex_file:
            if line == "\n":
                examples[service] = queries
                queries = []
                try:
                    service = ex_file.next().strip()
                    continue
                except StopIteration:
                    break

            queries.append(line.strip())

    return examples


def ghetto_classifier(params, my_service_holder):
    features = params['features']
    client = params['client']
    request_type = (features['questionType'] if 'questionType' in features
                        else features['actionType'])
    key = client, request_type
    # Pick the service with the highest confidence!
    conf_levels = {service_name: my_service_holder.services[service_name]
                    .run_heuristic(features['keywords'])
                    for service_name in my_service_holder.services}
    params['confidences'] = conf_levels
    params['service'] = (max(conf_levels, key=conf_levels.get) if
                         max(conf_levels.itervalues()) > 0 else "Unsorted")


def dict_to_file(my_service_data):
    name = my_service_data.name
    value_dict = my_service_data.values

    class Dummy_holder (object):
        def __init__(self, value):
            self.value = value
            self.names = []

    to_be_written = []
    dummy_dict = dict()

    for key in value_dict:
        if key.startswith("dummy_var"):
            if key not in dummy_dict:
                dummy_dict[key] = Dummy_holder(value_dict[key][0])
        elif str(value_dict[key][0]).startswith("dummy_var"):
            if value_dict[key][0] in dummy_dict:
                # If it is in the dummy_dict already, add it
                dummy_dict[value_dict[key][0]].names.append(key)
            else:
                # create a new entry to dummy_dict and add it
                dummy_dict[value_dict[key][0]] = Dummy_holder(
                    value_dict[value_dict[key][0]][0])

                dummy_dict[value_dict[key][0]].names.append(key)
        else:
            to_be_written.append(key + "," + str(value_dict[key][0]) + "\n")

    for key in dummy_dict:
        to_be_written.append('[\n')
        for entry in dummy_dict[key].names:
            to_be_written.append("    " + entry + "\n")
        to_be_written.append("], " + str(dummy_dict[key].value) + '\n')

    to_be_opened = path.realpath(
            path.join(
                path.dirname(__file__),
                'values_for_hill_climb',
                name + '_climbed_values.txt'))

    f = open(to_be_opened,"wb")
    for line in to_be_written:
        f.write(line)
    f.close()


def main():
    examples = parse_examples()
    my_service_holder = service_holder()

    services_to_step = climbing(examples, my_service_holder)

    counter = 0
    while len(services_to_step) > 0:
        my_service_holder.queries_are_good = False
        sys.stdout.flush()
        counter += 1
        for service in services_to_step:
            sys.stdout.flush()
            service_stepper(service, my_service_holder) # Steps the service
        services_to_step = climbing(examples, my_service_holder)
        if my_service_holder.queries_are_good == False:
            break
        # Write to file every 5th step, that way we don't lose too much
        # progress if we end early
        if counter % STEPS_BETWEEN_WRITES == 0:
            for service in my_service_holder.services:
                # Write to file
                dict_to_file(my_service_holder.services[service])

    for service in my_service_holder.services:
        # Write to file
        dict_to_file(my_service_holder.services[service])

    print "Success! You did it! Hills have been climbed!"


if __name__ == '__main__':
    main()
