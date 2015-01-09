# Movie heuristic
from Heuristic import Heuristic
class Movie_Heuristic(Heuristic):
    def __init__(self):
        INITIAL_VALUES = [75, 75, 75, 50, 60, 40, 60, 50, 50, 40, 40, 50, -50,
                            -50,-75, -60, -60, -90, -25, 30]
        super(Movie_Heuristic, self).__init__(INITIAL_VALUES)


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
    def run_heuristic(self, listOfVariableValues, extractedDict):
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
