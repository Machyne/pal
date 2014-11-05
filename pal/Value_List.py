import random
class Value_List:
    list_of_magnitudes = []
    list_of_directions = []

    def generate_variables(self,replaced):
        # If the last one was a new best, go in the same direction again
        if not replaced:
            for slot in self.list_of_directions:
                slot = random.randint(-1,1)

        # Generate new values
        SCALE_EFFECT = 1
        for item in xrange(self.list_of_magnitudes):
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


