# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from Value_List import *
import movie_heuristic

# Climbs hills towards better variables. Takes a list of processed
# queries (should be dictionaries) that are affirmative, a second list
# that contains negative queries and a duration for the number of times
# to hill climb.
def hill_climb(posDict, negDict, duration, init_values, service):
     # Create baseline
    list_of_values = Value_List(len(init_values))
    list_of_values.set_list_of_magnitudes(init_values)
    best = [list_of_values, get_score(posDict, negDict,
            list_of_values.get_magnitudes())]
    replaced = False

    # do the hill climbing
    count = 0
    while count <= duration:
        totalScore = get_score(posDict, negDict,
                               list_of_values.get_magnitudes(), service)
        if totalScore > best[1]:
            best[0] = list_of_values
            best[1] = totalScore
            replaced = True
        list_of_values.generate_variables(replaced)
        replaced = False
        count += 1
    return best


# Gets the total heuristic value for a given list of variables, and
# positive and negative dicts
def get_score(posDict, negDict, list_of_variables, service):
    toBeReturned = 0
    for extractedDict in posDict:
        toBeReturned += service.run_heuristic(list_of_variables,
                                              extractedDict)
    for extractedDict in negDict:
        toBeReturned += -1 * service.run_heuristic(list_of_variables,
                                                   extractedDict)
    return toBeReturned

# Hill climbing in a nutshell
# while True:
#     step listOfVariableValues
#     movie_heuristic.movieHeuristic()
#     if curValues > best:
#         best = cur

dummyDict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummyEVILDict = {'keywords': ['time', 'theatre'],
                 'Proper Nouns': ['SATAN', 'Satin']}

print movie_heuristic.movieHeuristic(movie_heuristic.INITIAL_VALUES, dummyDict)
temp = hill_climb([dummyDict], [dummyEVILDict], 10,
                  movie_heuristic.INITIAL_VALUES, movie_heuristic)

print temp[0].get_magnitudes()
