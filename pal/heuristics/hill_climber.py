# Runs an example heuristic
# Takes a feature extraction dictionary and returns a numerical value
# for the hueristic.

from pal.heuristics.value_vector import ValueVector


# Climbs hills towards better variables. Takes a list of extracted
# features (should be dictionaries) that are affirmative, a second list
# that contains negative queries, a duration for the number of times
# to hill climb. Also takes a list of keywords and an output file name,
# which are only used for printing hill climbed values with the
# associated variables in a new file.
def hill_climb(posDict, negDict, duration, init_values, service,
               keywords, output_file_name):
    # Create baseline
    vector_of_values = ValueVector(len(init_values))
    vector_of_values.set_list_of_magnitudes(init_values)
    best = [vector_of_values, get_score(posDict, negDict,
            service)]
    replaced = False

    # do the hill climbing
    count = 0
    while count <= duration:
        totalScore = get_score(posDict, negDict,
                               service)
        if totalScore > best[1]:
            best[0] = vector_of_values
            best[1] = totalScore
            replaced = True
        vector_of_values.generate_variables(replaced)
        replaced = False
        count += 1

    output_values = vector_of_values.get_magnitudes()
    output_file = open(output_file_name, 'wb')
    for line_number in xrange(len(keywords)):
        str_to_add = str(keywords[line_number]) + ','
        str_to_add += str(output_values[line_number]) + "\n"
        output_file.writelines(str_to_add)


# Gets the total heuristic value for a given list of variables, and
# positive and negative dicts
def get_score(posDict, negDict, service):
    toBeReturned = 0
    for extractedDict in posDict:
        toBeReturned += service.run_heuristic(extractedDict)
    for extractedDict in negDict:
        toBeReturned -= service.run_heuristic(list_of_variables,
                                              extractedDict)
    return toBeReturned
