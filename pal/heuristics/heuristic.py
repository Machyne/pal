import os
from collections import OrderedDict


class Heuristic(object):

    def __init__(self, heuristic_name):
        self._variables = OrderedDict()
        self._name = heuristic_name
        self.read_input_file()

    def _get_score(self, word):
        score = self._variables.get(word, 0)
        while isinstance(score, str):
            score = self._variables.get(score, 0)
        return score

    # Returns a heuristic value for a list of keywords
    def run_heuristic(self, keywords):
        return sum(self._get_score(word) for word in keywords)

    def read_input_file(self):
        # read input file into dictionary with keyword as key and
        # heuristic score as value
        file_ = os.path.join(
            *(os.path.split(os.path.realpath(__file__))[:-1] +
              (self._name + '_values.txt',)))
        with open(file_, 'rb') as input_file:
            dummy_count = 0
            in_list = False
            for i, line in enumerate(input_file):
                line = line.strip()
                if line.startswith('['):
                    if in_list:
                        raise SyntaxError(
                            'File "{}", line {}, nested lists not supported'
                            .format(input_file, i))
                    in_list = True
                    dummy_count += 1

                elif line.startswith(']'):
                    val = int(line.split(',')[1].strip())
                    self._variables['dummy_var_{}'.format(dummy_count)] = val

                elif in_list:
                    key = line.split(',')[0].strip()
                    self._variables[key] = 'dummy_var_{}'.format(dummy_count)

                elif ',' in line:
                    cur_line = map(str.strip, line.split(','))
                    self._variables[cur_line[0]] = int(cur_line[1])

    def get_input_list_values(self):
        return filter(lambda x: isinstance(x, int), self._variables.values())

    def _get_keys_from_value(self, val):
        return [k for k, v in self._variables.items() if v == val]

    def get_input_list_keywords(self):
        keys = filter(lambda x: isinstance(x[1], int), self._variables.items())
        return map(
            lambda x: (x[0] if not x[0].startswith('dummy_var_') else
                       self._get_keys_from_value(x[0])), keys)

    def climb_file_name(self):
        file_ = os.path.join(
            *(os.path.split(os.path.realpath(__file__))[:-1] +
              ('climbed_{}_values.txt'.format(self._name),)))
        return file_

if __name__ == '__main__':
    my_heur = Heuristic('movie')
    print my_heur.get_input_list_keywords()
    my_heur = Heuristic('stalkernet')
    print my_heur.get_input_list_keywords()
