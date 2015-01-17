from heuristic import Heuristic


class StalkernetHeuristic(Heuristic):
    def __init__(self):
        self.input_list = []
        self.read_input_file()
        super(StalkernetHeuristic, self).__init__(self.input_list)

    # Returns a heuristic value for a list of keywords
    def run_heuristic(self, keywords):
        toBeReturned = 0
        for word in keywords:
            if word in self.input_list:
                toBeReturned += self.input_list[word]
        return toBeReturned

    def read_input_file(self):
        # read input file into dictionary with keyword as key and
        # heuristic score as value
        input_file = open('stalkernet_values.txt', 'rb')
        for line in input_file:
            cur_line = line.split(',')
            self.input_list += [(cur_line[0], int(cur_line[1]))]

if __name__ == '__main__':
    my_heuristic = StalkernetHeuristic()
    print my_heuristic.list_of_values.get_magnitudes()
