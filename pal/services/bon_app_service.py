#!usr/bin/env python
# A service for the dining hall menus

from datetime import date
from datetime import timedelta

from api.food.bon_api import BonAPI
from pal.services.service import Service


def wrap_response(func):
    def wrapped(features):
        return {'response': func(features)}
    return wrapped

BURTON = 'burton-hall'
LDC = 'east-hall'
SAYLES = 'sayles-hill-cafe'


class BonAppetitService(Service):

    cafe_keywords = {'ldc': LDC,
                     'east': LDC,
                     'burton': BURTON,
                     'sayles': SAYLES,
                     'sayles-hill': SAYLES,
                     'weitz': "weitz-cafe"}
    meal_keywords = {'breakfast', 'brunch', 'lunch', 'dinner'}
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday']
    date_keywords = {'today', 'tomorrow'}.union(set(weekdays))

    def infer_date(self, date_word):
        """ Given a day string, return a corresponding python date object """
        date_word = date_word.lower()
        current_date = date.today()
        if date_word == "today" or date_word is None:
            return current_date
        if date_word == "tomorrow":
            tomorrow = current_date + timedelta(days=1)
            return tomorrow
        if date_word in self.weekdays:
            desired_day = self.weekdays.index(date_word)
            current_day = current_date.weekday()
            days_in_future = (desired_day - current_day) % 7
            return current_date + timedelta(days=days_in_future)

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
        formatted_station = "{title}:\n{items}\n"
        formatted_item = "{label}\n"
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
                items = ""
                items_list = station_details.get(u'items', [])
                for item in items_list:
                    if type(item) == dict:
                        label = item.get(u'label', u'food item')
                        items += formatted_item.format(label=label)
                    # Some items are just ID strings,
                    # not sure what to do with those.
                stations += formatted_station.format(title=station,
                                                     items=items)
            meals += formatted_meal.format(meal_name=meal,
                                           start=start,
                                           end=end,
                                           stations=stations)

        return formatted_response.format(cafe=cafe, meals=meals)

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return 1

    @wrap_response
    def go(self, features):
        api = BonAPI()

        tagged_nouns = features.get('nouns', [])
        keywords = features.get('keywords', [])

        nouns = [tagged[0].lower() for tagged in tagged_nouns]

        extracted_keywords = set(nouns + keywords)

        def matching_keywords(my_keyword_set):
            return my_keyword_set.intersection(extracted_keywords) or None

        day_matches = matching_keywords(self.date_keywords)
        if len(day_matches) > 1:
            return "I can only display results for a single day."
        day = self.infer_date(day_matches[0] if day_matches else None)

        cafe_matches = matching_keywords(set(self.cafe_keywords.keys()))
        if len(cafe_matches) != 1:
            return ("I can only display results for "
                    "a single Bon Appetit location.")
        cafe = self.infer_cafe(cafe_matches[0])

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
