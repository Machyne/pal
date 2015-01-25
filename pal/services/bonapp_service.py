# A service for the dining hall menus

from api import DataNotAvailableException
from api.bonapp.bon_api import get_meals_for_cafe
from pal.services.service import Service
from utils import infer_date
from utils import weekdays


def wrap_response(func):
    return lambda *args: {'response': func(*args)}

LDC = "east-hall"
BURTON = "burton"
SAYLES = "sayles-hill-cafe"
WEITZ = "weitz-cafe"


class BonAppService(Service):

    cafe_keywords = {'ldc': LDC,
                     'east': LDC,
                     'burton': BURTON,
                     'sayles': SAYLES,
                     'sayles-hill': SAYLES,
                     'weitz': WEITZ}
    reverse_lookup_cafes = {
        LDC: "East Dining Hall",
        'burton': "Burton Dining Hall",
        SAYLES: "Sayles-Hill Cafe",
        WEITZ: "Weitz Cafe"
    }
    meal_keywords = {'breakfast', 'brunch', 'lunch', 'dinner'}
    date_keywords = {'today', 'tomorrow'}.union(set(weekdays))
    requested_cafe = None

    def infer_cafe(self, colloquial):
        """ Maps the colloquial cafe names to Bon Appetit's names """
        inferred = self.cafe_keywords[colloquial]
        self.requested_cafe = inferred
        return inferred

    def _parse_string_from_response(self, api_response, requested_meals):
        """ Builds a human-readable string from the API response dictionary """
        # TODO: if the user asks for lunch on the weekend,
        # give them the brunch data
        if requested_meals is None or len(requested_meals) == 0:
            requested_meals = self.meal_keywords
        # FIXME: This html is hopefully temporary
        formatted_response = "Location: {cafe}<ul>{meals}</ul>"
        cafe = self.reverse_lookup_cafes[self.requested_cafe]
        formatted_meal = ("<li>{meal_name}: {hours}"
                          "<ul>{stations}</ul></li>")
        formatted_station = "<li>{title}:<ul>{entrees}</ul></li>"
        formatted_entree = "<li>{label}</li>"
        meals = ""
        for meal, meal_details in api_response.iteritems():
            if meal.lower() not in requested_meals:
                continue
            stations = ""
            hours = meal_details[u'time_formatted']
            stations_dict = meal_details.get(u'stations', {})
            for station, station_details in (stations_dict.iteritems()):
                entrees = ""
                entrees_list = station_details.get(u'items', [])
                for entree in entrees_list:
                    if type(entree) == dict:
                        label = entree.get(u'label', u'entree')
                        entrees += formatted_entree.format(label=label)
                    # Some entrees are just ID strings,
                    # not sure what to do with those.
                stations += formatted_station.format(title=station,
                                                     entrees=entrees)
            meals += formatted_meal.format(meal_name=meal,
                                           hours=hours,
                                           stations=stations)

        return formatted_response.format(cafe=cafe, meals=meals)

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, features):

        tagged_nouns = features.get('nouns', [])
        keywords = features.get('keywords', [])

        nouns = [tagged[0].lower() for tagged in tagged_nouns]

        extracted_keywords = set(nouns + keywords)

        def matching_keywords(my_keyword_set):
            return my_keyword_set.intersection(extracted_keywords)

        day_matches = matching_keywords(self.date_keywords)
        if len(day_matches) > 1:
            return "I can only display results for a single day."
        day = infer_date(day_matches.pop() if day_matches else "today")

        cafe_matches = matching_keywords(set(self.cafe_keywords.keys()))
        if len(cafe_matches) != 1:
            return ("I can only display results for "
                    "a single Bon Appetit location.")
        cafe = self.infer_cafe(cafe_matches.pop())

        meal_matches = matching_keywords(self.meal_keywords) or set()

        try:
            api_response = get_meals_for_cafe(cafe, day)
        except DataNotAvailableException:
            return ("I'm sorry, Bon Appetit doesn't appear to have any "
                    "specials for {cafe} on {date_}.".format(
                        cafe=self.reverse_lookup_cafes[cafe],
                        date_=day.strftime("%d/%m/%y")))

        if meal_matches is not None:
            # Handle some edge cases for meal/cafe/day combinations
            if "brunch" in meal_matches and day.weekday() < 5:
                # weekday 5 is Saturday
                return "Brunch is only served on the weekend."
            if "breakfast" in meal_matches:
                if day.weekday() == 5 and cafe != LDC:
                    return ("Breakfast is only served at "
                            "East Hall (LDC) on Saturday.")
                if day.weekday() == 6:
                    return "Breakfast isn't served on Sunday."
            if "lunch" in meal_matches and day.weekday() < 5:
                # If the user is asking for lunch on the weekend, assume
                # brunch data will satisfy them
                meal_matches.remove("lunch")
                meal_matches.add("brunch")

        return self._parse_string_from_response(api_response,
                                                meal_matches)
