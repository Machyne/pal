import requests
import json
import datetime

from pal.services.service import Service


class ForeCastNotAvailableException(Exception):
    pass


class WeatherService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    def go(self, features):

        places = [place[0] for place in features['tree'] if place[1] == 'GPE']
        orgs = [org[0] for org in features['tree'] if org[1] == 'ORGANIZATION']
        nouns = features['nouns']
        keywords = features['keywords']
        if len(places) == 1:
            city = places[0]

            state = None
            # country = None
            if len(orgs) == 1:
                state = orgs[0]
            # if len(orgs) == 2:
            #     state = orgs[1]
            #     country = orgs[2]

            # query Yahoo
            baseurl = "https://query.yahooapis.com/v1/public/yql?"

            if state is not None:
                # doing a terrible thing and assuing everything is in the US
                state_str = "US-" + state
                yql_query = ("select * from weather.forecast where woeid in "
                             "(select woeid from geo.places where "
                             "text=\"{0}\" and "
                             "admin1.code=\"{1}\")").format(city, state_str)
            else:
                yql_query = ("select * from weather.forecast where woeid in "
                             "(select woeid from geo.places(1) where "
                             "text=\"{0}\")").format(city)
            print yql_query
            payload = {'q': yql_query, 'format': 'json'}
            response = requests.post(baseurl, params=payload)
            response_json = json.loads(response.text)
            # print response_json

            # try to find day
            noun_words = [noun[0].lower() for noun in nouns]
            days = set(['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday', 'tomorrow'])
            intersect = days.intersection(set(noun_words))

            # remember if the user asked about today/tomorrow for more natural
            # result output language
            isToday = False
            isTomorrow = False

            if len(intersect) == 0:
                # assume the user is asking about today
                now = datetime.datetime.now()
                day = now.strftime("%A").lower()
                isToday = True
            else:
                day = intersect.pop()

            if day == 'tomorrow':
                # handle tomorrow
                now = datetime.datetime.now()
                tomorrow = now + datetime.timedelta(days=1)
                day = tomorrow.strftime("%A").lower()
                isTomorrow = True

            yahoo_days = {"monday": "Mon", "tuesday": "Tue",
                          "wednesday": "Wed", "thursday": "Thu",
                          "friday": "Fri", "saturday": "Sat", "sunday": "Sun"}

            try:
                forecasts = response_json['query']['results']['channel']
                # 80 char line limit..
                forecasts = forecasts['item']['forecast']
            except Exception, e:
                raise e

            yahoo_day = yahoo_days[day]
            days_forecast = [f for f in forecasts if f['day'] == yahoo_day]
            if len(days_forecast) > 0:
                day_forecast = days_forecast[0]
            else:
                return {'response':
                        ("Weather information not available for "
                         "{0} on {1}").format(city, day.title())}

            high_temp = day_forecast['high']
            low_temp = day_forecast['low']

            response = ""

            if 'high' in keywords:
                response = ("The high for {0} will "
                            "be {1} degrees").format(day.title(), high_temp)
            elif 'low' in keywords:
                response = ("The low for {0} will "
                            "be {1} degrees").format(day.title(), low_temp)
            else:
                response = ("The high for {0} will be {1} degrees and the low "
                            "will be {2} "
                            "degrees").format(day.title(), high_temp, low_temp)
            return {'response': response}

        else:
            # more than one or no GPE found... now what?
            pass
        # if place
