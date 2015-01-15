#!usr/bin/env python
# A service for the dining hall menus

from datetime import date
from datetime import timedelta

from api.food.bon_api import BonAPI
from pal.services.service import Service


class BonAppetitService(Service):

    cafe_keywords = {'ldc': "east-hall",
                     'east': "east-hall",
                     'burton': "burton-hall",
                     'sayles': "sayles-hill-cafe",
                     'sayles-hill': "sayles-hill-cafe",
                     'weitz': "weitz-cafe"}
    # TODO: meal_keywords = {'breakfast', 'brunch', 'lunch', 'dinner'}
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday']
    date_keywords = {'today', 'tomorrow'}.union(set(weekdays))

    def matching_keywords(self, my_keyword_set, extracted_keyword_set):
        return my_keyword_set.intersection(extracted_keyword_set) or None

    def infer_date(self, date_word):
        """ Given a day string, return a corresponding
        date object.
        """
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

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return 1

    def go(self, features):
        api = BonAPI()

        tagged_nouns = features.get('nouns', [])
        keywords = features.get('keywords', [])
        question_type = features.get('questionType', None)

        nouns = [tagged[0].lower() for tagged in tagged_nouns]

        extracted_keywords = set(nouns + keywords)

        days = self.matching_keywords(self.date_keywords, extracted_keywords)
        day = self.infer_date(days[0] if days else None)

        cafe_matches = self.matching_keywords(set(self.cafe_keywords.keys()),
                                              extracted_keywords)
        results = []
        for cafe in cafe_matches:
            results.append(api.get_data(self.cafe_keywords[cafe], day))
