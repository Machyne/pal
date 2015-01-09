# Value_Vectors contain a list of magnitudes and a direction for each
# magnitude.

import random
has_color = False
try:
    import color
    has_color = True
except ImportError:
    pass

class Value_Vector:

    def __init__(self,num_values):
        self.list_of_magnitudes = [0] * num_values
        self.list_of_directions = [0] * num_values

    def __repr__(self):
        if has_color:
            color_string = ""
            for item in xrange(len(self.list_of_magnitudes)):
                if self.list_of_directions[item] == -1:
                    color_string += color.Colors.red + \
                        str(self.list_of_magnitudes[item]) + color.Colors.white
                elif self.list_of_directions[item] == 0:
                    color_string += color.Colors.white + \
                        str(self.list_of_magnitudes[item])
                else:
                    color_string += color.Colors.green + \
                        str(self.list_of_magnitudes[item]) + color.Colors.white
                color_string += ', '
            return color_string
        else:
            return_string = ""
            for item in xrange(len(self.list_of_magnitudes)):
                return_string += '(' + str(self.list_of_magnitudes[item]) + ',' +\
                    str(self.list_of_directions[item]) + ')' + ', '
            return return_string

    def generate_variables(self,replaced):
        # If the last one was a new best, go in the same direction again
        if not replaced:
            for slot in xrange(len(self.list_of_directions)):
                self.list_of_directions[slot] = random.randint(-1,1)

        # Generate new values
        SCALE_EFFECT = 1
        for item in xrange(len(self.list_of_magnitudes)):
            self.list_of_magnitudes[item] += (self.list_of_directions[item] *
                                                SCALE_EFFECT)

    # Sets self.list_of_magnitudes to be equal to magnitudes
    def set_list_of_magnitudes(self, magnitudes):
        self.list_of_magnitudes = magnitudes

    # Sets self.list_of_directions to be equal to directions
    def set_list_of_directions(self,directions):
        self.list_of_directions = directions

    def get_magnitudes(self):
        return self.list_of_magnitudes

    def get_directions(self):
        return self.list_of_directions

if __name__ == '__main__':
    main()

def main():
    test = Value_Vector(5)
    test.generate_variables(False)
    test.generate_variables(True)
    test.generate_variables(True)
    test.generate_variables(True)
    test.generate_variables(True)

    print test
