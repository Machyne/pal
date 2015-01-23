#!usr/bin/env python
# A service for the dining hall menus


from api.food.bon_api import BonAPI
from pal.services.service import Service
from utils import infer_date
from utils import weekdays


def wrap_response(func):
    return lambda *args: {'response': func(*args)}

LDC = 'east-hall'
SAYLES = 'sayles-hill-cafe'


class BonAppetitService(Service):

    cafe_keywords = {'ldc': LDC,
                     'east': LDC,
                     'burton': 'burton',
                     'sayles': SAYLES,
                     'sayles-hill': SAYLES,
                     'weitz': "weitz-cafe"}
    meal_keywords = {'breakfast', 'brunch', 'lunch', 'dinner'}
    date_keywords = {'today', 'tomorrow'}.union(set(weekdays))

    def infer_cafe(self, colloquial):
        """ Maps the colloquial cafe names to Bon Appetit's names """
        return self.cafe_keywords[colloquial]

    def parse_string_from_response(self, api_response, requested_meals):
        """ Builds a human-readable string from the API response dictionary """
        if requested_meals is None:
            requested_meals = self.meal_keywords
        formatted_response = "Cafe: {cafe}\n{meals}\n"
        cafe = api_response.get(u'current_cafe', {}).get(u'name', 'cafe')
        formatted_meal = "{meal_name}: {start}-{end}\n{stations}\n"
        formatted_station = "{title}:\n{entrees}\n"
        formatted_entree = "{label}\n"
        meals = ""
        dayparts = api_response.get(u'dayparts', {})
        for meal, meal_details in dayparts.iteritems():
            if meal.lower() not in requested_meals:
                continue
            stations = ""
            start = meal_details.get(u'starttime', u'NA')
            end = meal_details.get(u'endtime', u'NA')
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
                                           start=start,
                                           end=end,
                                           stations=stations)

        return formatted_response.format(cafe=cafe, meals=meals)

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, features):
        api = BonAPI()

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

        meal_matches = matching_keywords(self.meal_keywords)

        api_response = api.get_data(cafe, day)

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

        return self.parse_string_from_response(api_response,
                                               meal_matches)
