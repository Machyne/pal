# This is the abstract class for a heuristic

from value_vector import Value_Vector


class Heuristic(object):
    # Takes a list of lists  of keyword, value pairs. Then  creates a
    # heuristic object
    def __init__(self, value_list):
        self.list_of_values = Value_Vector(len(value_list))
        magnitude_list = []
        for item in value_list:
            magnitude_list += [item[1]]
        self.list_of_values.set_list_of_magnitudes(magnitude_list)

    def run_heuristic(self, list_of_variable_values, extracted_dict):
        # Returns a heuristic value for an extracted dict, given a list of
        # variable values.
        return 0

if __name__ == '__main__':
    my_heur = Heuristic([["a",1],["b",2],["c",3]])
    print my_heur.list_of_values.get_magnitudes()
