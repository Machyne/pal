# Movie heuristic
from pal.heuristics.heuristic import Heuristic


class MovieHeuristic(Heuristic):
    def __init__(self):
        self.input_list = []
        self.read_input_file()
        super(MovieHeuristic, self).__init__(self.input_list)

    # Returns a heuristic value for a list of keywords
    def run_heuristic(self, keywords):
        to_be_returned = 0
        for word in keywords:
            if word in self.input_list:
                to_be_returned += self.input_list[word]
        return to_be_returned

    def read_input_file(self):
        # read input file into dictionary with keyword as key and
        # heuristic score as value
        input_file = open('movie_values.txt', 'rb')
        for line in input_file:
            cur_line = line.split(',')
            self.input_list += [(cur_line[0], int(cur_line[1]))]

    def get_input_list_values(self):
        to_be_returned = []
        for item in self.input_list:
            to_be_returned += [item[1]]
        return to_be_returned

    def get_input_list_keywords(self):
        to_be_returned = []
        for item in self.input_list:
            to_be_returned += [item[0]]
        return to_be_returned


if __name__ == '__main__':
    my_heuristic = MovieHeuristic()
    print my_heuristic.list_of_values.get_magnitudes()
