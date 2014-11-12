# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from Value_List import *

# Movie heuristic

# Returns a heuristic value for an extracted dict, given a list of
# variable values.
#
# listOfVariableValues
#   0  - Movie
#   1  - Film
#   2  - Movies
#   3  - hasProperNouns
#   4  - actor/acted/actress
#   5  - Released
#   6  - Rating/Review
#   7  - Plot
#   8  - lead/leads
#   9  - Genre
#   10 - Produce*
#   11 - Writer/Written/Wrote
#   12 - Ticket
#   13 - Purchase/Buy
#   14 - Time
#   15 - Showing
#   16 - Playing
#   17 - Where
#   18 - Theater/Theatre
#   19 - Story
def movieHeuristic(listOfVariableValues, extractedDict):
    toBeReturned = 0
    if "Movie" in extractedDict['keywords'] or\
            "movie" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[0]

    if "Film" in extractedDict['keywords'] or\
            "film" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[1]

    if "Movies" in extractedDict['keywords'] or\
            "movies" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[2]

    if extractedDict['Proper Nouns']:
        toBeReturned += listOfVariableValues[3]

    if "actor" in extractedDict['keywords'] or\
            "acted" in extractedDict['keywords'] or\
            "act" in extractedDict['keywords'] or\
            "actress" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[4]

    if "released" in extractedDict['keywords'] or\
            "Released" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[5]

    if "Rating" in extractedDict['keywords'] or\
            "rating" in extractedDict['keywords'] or\
            "Review" in extractedDict['keywords'] or\
            "review" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[6]

    if "plot" in extractedDict['keywords'] or\
            "Plot" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[7]

    if "lead" in extractedDict['keywords'] or\
            "Lead" in extractedDict['keywords'] or\
            "leads" in extractedDict['keywords'] or\
            "Leads" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[8]

    if "Genre" in extractedDict['keywords'] or\
            "genre" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[9]

    if "Produce" in extractedDict['keywords'] or\
            "Producer" in extractedDict['keywords'] or\
            "Produced" in extractedDict['keywords'] or\
            "produce" in extractedDict['keywords'] or\
            "produced" in extractedDict['keywords'] or\
            "producer" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[10]

    if "Writer" in extractedDict['keywords'] or\
            "Written" in extractedDict['keywords'] or\
            "Wrote" in extractedDict['keywords'] or\
            "writer" in extractedDict['keywords'] or\
            "written" in extractedDict['keywords'] or\
            "wrote" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[11]

    if "Ticket" in extractedDict['keywords'] or\
            "ticket" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[12]

    if "Purchase" in extractedDict['keywords'] or\
            "purchase" in extractedDict['keywords'] or\
            "Buy" in extractedDict['keywords'] or\
            "buy" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[13]

    if "Time" in extractedDict['keywords'] or\
            "time" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[14]

    if "Showing" in extractedDict['keywords'] or\
            "showing" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[15]

    if "Playing" in extractedDict['keywords'] or\
            "playing" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[16]

    if "Where" in extractedDict['keywords'] or\
            "where" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[17]

    if "Theater" in extractedDict['keywords'] or\
            "theater" in extractedDict['keywords'] or\
            "Theatre" in extractedDict['keywords'] or\
            "theatre" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[18]

    if "Story" in extractedDict['keywords'] or\
            "story" in extractedDict['keywords']:
        toBeReturned += listOfVariableValues[19]

    return toBeReturned

# Climbs hills towards better variables. Takes a
def hill_climb(posDict, negDict, duration):
    INITIAL_VALUES = [75, 75, 75, 50, 60, 40, 60, 50, 50, 40, 40, 50, -50, -50,
                      -75, -60, -60, -90, -25, 30]

    # Create baseline
    list_of_values = Value_List(len(INITIAL_VALUES))
    list_of_values.set_list_of_magnitudes(INITIAL_VALUES)
    best = [list_of_values, get_score(posDict, negDict,
            list_of_values.get_magnitudes())]
    replaced = False

    # do the hill climbing
    count = 0
    while count <= duration:
        totalScore = get_score(posDict, negDict,
                               list_of_values.get_magnitudes())
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
def get_score(posDict, negDict, list_of_variables):
    toBeReturned = 0
    for extractedDict in posDict:
        toBeReturned += movieHeuristic(list_of_variables, extractedDict)
    for extractedDict in negDict:
        toBeReturned += -1 * movieHeuristic(list_of_variables, extractedDict)
    return toBeReturned


# Hill climbing in a nutshell
# while True:
#     step listOfVariableValues
#     movieHeuristic()
#     if curValues > best:
#         best = cur

dummyDict = {'keywords': ['Movie', 'actor'], 'Proper Nouns': ['Tom Hanks']}
dummyEVILDict = {'keywords': ['time', 'theatre'],
                 'Proper Nouns': ['SATAN', 'Satin']}
INITIAL_VALUES = [75, 75, 75, 50, 60, 40, 60, 50, 50, 40, 40, 50, -50, -50,
                  -75, -60, -60, -90, -25, 30]

print movieHeuristic(INITIAL_VALUES, dummyDict)
print hill_climb([dummyDict], [dummyEVILDict], 100)
