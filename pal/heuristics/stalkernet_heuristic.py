from pal.heuristics.heuristic import Heuristic


class StalkernetHeuristic(Heuristic):
    INITIAL_VALUES = [10, 10, 10, 50, 30, 40, 20, 60, 40, 30, 40, 30, -20, -20,
                      -40, 70]

    def __init__(self, arg):
        super(StalkernetHeuristic, self).__init__(INITIAL_VALUES)

    # Returns a heuristic value for an extracted dict, given a list of
    # variable values.
    #
    # listOfVariableValues
    # 0   - Where
    # 1   - Who
    # 2   - Which
    # 3   - Proper Nouns
    # 4   - Major
    # 5   - Live
    # 6   - Office
    # 7   - Roommate
    # 8   - Graduate
    # 9   - Faculty
    # 10  - Department
    # 11  - Building
    # 12  - Call
    # 13  - Contact
    # 14  - Eat
    # 15  - ALL OF THE BUILDINGS
    def run_heuristic(self, list_of_variable_values, extracted_dict):
        toBeReturned = 0
        if "Where" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[0]

        if "Who" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[1]

        if "Which" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[2]

        if "Proper Nouns" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[3]

        if "Major" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[4]

        if "Live" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[5]

        if "Office" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[6]

        if "Roommate" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[7]

        if "Graduate" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[8]

        if "Faculty" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[9]

        if "Department" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[10]

        if "Building" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[11]

        if "Call" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[12]

        if "Contact" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[13]

        if "Eat" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[14]

        if "Benton" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Berg" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Bird" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Boliou" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Brooks" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Burton" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Cassat" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Center for Math & Computing" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "CMC" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Chaney" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Clader" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Collier" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Colwell" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Cowling Gymnasium" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Cowling" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Dacie Moses" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Davis" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Dixon" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Douglas" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Dow" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "LDC" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Eugster" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Evans" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Facilities" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Facilities Building" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Faculty Club" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Fac Club" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Farm" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Geffert" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Goodhue" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Goodsell" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Goodsell Observatory" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Gould Library" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Library" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Libe" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Grounds Garage/Warehouse" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hall" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Henrickson" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Henry" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hill" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hoppin" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hulings" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hunt Cottage" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Hunt" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Huntington" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "James" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Jewett" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Johnson" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Laird" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Laird Stadium" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Stadium" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Leighton" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Memo" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Mudd" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Music & Drama Center" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Music Hall" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Musser" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Myers" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Nason" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Nourse" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Nutting" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Olin" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Owens" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Page House East" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Page House West" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Parish" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Parr" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Prentice" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Recreation Center" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Rec" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Rice" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Sayles-Hill Campus Center" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Sayles" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Scott" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Scoville" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Severance" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Skinner Memorial Chapel" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Chapel" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Stimson" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Strong" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Twin Cities Office" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Watson" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Weitz Center for Creativity" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Weitz" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "West Gymnasium" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Williams" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Willis" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Wilson" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Allen" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "Arb" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        if "200 Division Street" in extracted_dict['keywords']:
            toBeReturned += list_of_variable_values[15]

        return toBeReturned
