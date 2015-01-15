# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from pal.heuristics.hill_climb_heuristic import hill_climb
from pal.heuristics.movie_heuristic import MovieHeuristic

# Hill climbing in a nutshell
# while True:
#     step listOfVariableValues
#     movie_heuristic.movieHeuristic()
#     if curValues > best:
#         best = cur
# asdf

dummyDict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummyEVILDict = {'keywords': ['time', 'theatre'],
                 'Proper Nouns': ['SATAN', 'Satin']}

myHeuristic = MovieHeuristic()
temp = hill_climb([dummyDict], [dummyEVILDict], 50, [75, 75, 75, 50, 60, 40,
                                                     60, 50, 50, 40, 40, 50,
                                                     -50, -50, -75, -60, -60,
                                                     -90, -25, 30],
                  myHeuristic)

print temp[0].get_magnitudes()

temp = hill_climb([dummyDict], [dummyEVILDict], 50, temp[0].get_magnitudes(),
                  myHeuristic)

print temp[0].get_magnitudes()
