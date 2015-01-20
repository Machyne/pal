# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from pal.heuristics.hill_climber import hill_climb
from pal.heuristics.heuristic import Heuristic


dummy_dict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummy_evil_dict = {'keywords': ['time', 'theatre'],
                   'Proper Nouns': ['SATAN', 'Satin']}


if __name__ == '__main__':
    heuristic = Heuristic('movie')
    hill_climb([dummy_dict], [dummy_evil_dict], 100, heuristic)
    heuristic = Heuristic('stalkernet')
    hill_climb([dummy_dict], [dummy_evil_dict], 100, heuristic)
