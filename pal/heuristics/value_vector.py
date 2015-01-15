# Value_Vectors contain a list of magnitudes and a direction for each
# magnitude.

import random
has_color = False
try:
    from pal.heuristics.color import Colors
    has_color = True
except ImportError:
    pass


class ValueVector(object):

    def __init__(self, num_values):
        self.list_of_magnitudes = [0] * num_values
        self.list_of_directions = [0] * num_values
        self.itr_count = 0

    def __repr__(self):
        if has_color:
            color_string = ""
            for item in xrange(len(self.list_of_magnitudes)):
                if self.list_of_directions[item] == -1:
                    color_string += Colors.red + \
                        str(self.list_of_magnitudes[item]) + Colors.white
                elif self.list_of_directions[item] == 0:
                    color_string += Colors.white + \
                        str(self.list_of_magnitudes[item])
                else:
                    color_string += Colors.green + \
                        str(self.list_of_magnitudes[item]) + Colors.white
                color_string += ', '
            return color_string
        else:
            return_string = ""
            for item in xrange(len(self.list_of_magnitudes)):
                return_string += '(' + str(self.list_of_magnitudes[item]) + ',' +\
                    str(self.list_of_directions[item]) + ')' + ', '
            return return_string

    # Updates the magnitudes with new ones. "replaced" is true when the
    # previous step was in a direction that led to a higher heuristic
    # value. Otherwise, it is false. If "replaced" is true, then
    # climbing continues in the same direction. Otherwise, random
    # directions are generated.
    def generate_variables(self, replaced):
        # If the last one was a new best, go in the same direction again
        if not replaced:
            for slot in xrange(len(self.list_of_directions)):
                self.list_of_directions[slot] = random.randint(-1, 1)
        self.itr_count += 1
        # Generate new values
        SCALE_EFFECT = self.get_scaling()
        for item in xrange(len(self.list_of_magnitudes)):
            self.list_of_magnitudes[item] += (self.list_of_directions[item] *
                                              SCALE_EFFECT)

    # Sets self.list_of_magnitudes to be equal to magnitudes
    def set_list_of_magnitudes(self, magnitudes):
        self.list_of_magnitudes = magnitudes

    # Sets self.list_of_directions to be equal to directions
    def set_list_of_directions(self, directions):
        self.list_of_directions = directions

    def get_magnitudes(self):
        return self.list_of_magnitudes

    def get_directions(self):
        return self.list_of_directions

    # generates an interger to use for the scaling effect?
    def get_scaling(self):
        return 1


def main():
    test = ValueVector(5)
    test.generate_variables(False)
    test.generate_variables(True)
    test.generate_variables(True)
    test.generate_variables(True)
    test.generate_variables(True)
    print test


if __name__ == '__main__':
    main()
