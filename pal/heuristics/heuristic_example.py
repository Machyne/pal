# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from pal.heuristics.hill_climber import hill_climb
from pal.heuristics.movie_heuristic import MovieHeuristic

# Hill climbing in a nutshell
# while True:
#     step listOfVariableValues
#     movie_heuristic.movieHeuristic()
#     if curValues > best:
#         best = cur

dummyDict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummyEVILDict = {'keywords': ['time', 'theatre'],
                 'Proper Nouns': ['SATAN', 'Satin']}


myHeuristic = MovieHeuristic()
keywords = myHeuristic.get_input_list_keywords()

hill_climb([dummyDict], [dummyEVILDict], 100,
           myHeuristic.get_input_list_values(), myHeuristic,
           keywords, 'climbed_movie_values.txt')
