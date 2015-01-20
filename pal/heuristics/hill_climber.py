# Takes a feature extraction dictionary and returns a numerical value
# for the heuristic.

from pal.heuristics.value_vector import ValueVector


# Climbs hills towards better variables. Takes a list of extracted
# features (should be dictionaries) that are affirmative, a second list
# that contains negative queries, a duration for the number of times
# to hill climb, and the heuristic to use.
def hill_climb(pos_dict, neg_dict, duration, heuristic):
    # Create baseline
    magnitude_list = heuristic.get_input_list_values()
    vector_of_values = ValueVector(len(magnitude_list))
    vector_of_values.set_list_of_magnitudes(magnitude_list)

    best = [vector_of_values, _get_score(pos_dict, neg_dict, heuristic)]
    replaced = False

    # do the hill climbing
    count = 0
    while count <= duration:
        totalScore = _get_score(pos_dict, neg_dict, heuristic)
        if totalScore > best[1]:
            best[0] = vector_of_values
            best[1] = totalScore
            replaced = True
        vector_of_values.generate_variables(replaced)
        replaced = False
        count += 1

    output_values = vector_of_values.get_magnitudes()
    with open(heuristic.climb_file_name, 'wb+') as output_file:
        for i, key in enumerate(heuristic.get_input_list_keywords()):
            val = output_values[i]
            if isinstance(key, str):
                output_file.writelines('{}, {}\n'.format(key, val))
            else:
                kws = '\n'.join(map(lambda k: ' ' * 4 + k, key))
                output_file.writelines('[\n{}\n], {}\n'.format(kws, val))


# Gets the total heuristic value for a given list of variables, and
# positive and negative dicts
def _get_score(pos_dict, neg_dict, heuristic):
    score = sum(heuristic.run_heuristic(dict_) for dict_ in pos_dict)
    score -= sum(heuristic.run_heuristic(dict_) for dict_ in neg_dict)
    return score
