# This is the abstract class for a heuristic

from value_vector import ValueVector


class Heuristic(object):
    # Takes a list of initial values, and creates a heuristic object
    def __init__(self, init_values):
        self.list_of_values = Value_Vector(len(init_values))
        self.list_of_values.set_list_of_magnitudes(init_values)

    def run_heuristic(self, list_of_variable_values, extracted_dict):
        # Returns a heuristic value for an extracted dict, given a list of
        # variable values.
        return 0
