# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from hill_climb_heuristic import *
from movie_heuristic import *

# Hill climbing in a nutshell
# while True:
#     step listOfVariableValues
#     movie_heuristic.movieHeuristic()
#     if curValues > best:
#         best = cur

dummyDict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummyEVILDict = {'keywords': ['time', 'theatre'],
                 'Proper Nouns': ['SATAN', 'Satin']}

myHeuristic = Movie_Heuristic()
temp = hill_climb([dummyDict], [dummyEVILDict], 50, [75, 75, 75, 50, 60, 40,
            60, 50, 50, 40, 40, 50, -50,-50,-75, -60, -60, -90, -25, 30], \
            myHeuristic)

print temp[0].get_magnitudes()

temp = hill_climb([dummyDict], [dummyEVILDict], 50, temp[0].get_magnitudes(),\
    myHeuristic)

print temp[0].get_magnitudes()
