#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

import datetime

import requests

from pal.services.base_service import Service
from pal.services.base_service import wrap_response


class WeatherService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        return super(self.__class__, self).get_confidence(params)

    @wrap_response
    def go(self, params):
        features = params['features']
        location = None
        places = None
        state = None
        city = None
        if 'location' in params.get('user-data', {}):
            location = params['user-data']['location']
        elif 'location' in params.get('client-data', {}):
            location = params['client-data']['location']
        # Why are there so many types of things that a location can be tagged
        # as? GPE = Geo-Political Entity; GSP = "Geo-Socio-Political group"
        places = [place[0] for place in features['tree'] if place[1] in
              ['GPE', 'GSP', 'LOCATION', 'PERSON']]
        orgs = [org[0] for org in features['tree'] 
                if org[1] == 'ORGANIZATION']
        tokens = set([t[0].lower() for t in features['tree']])

        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        if location or places:
            if location:
                # get the city name, woeid
                coords = location.split(',')
                city_query = ("select city, woeid from geo.placefinder(1) "
                              " where text=\"{0},{1}\" and gflags=\"R\""
                              ).format(coords[0], coords[1])
                city_payload = {'q': city_query, 'format': 'json'}
                city_response = requests.post(baseurl, city_payload)
                woeid = None
                try:
                    city_json = city_response.json()
                    city_result = city_json['query']['results']['Result']
                    city = city_result['city']
                    woeid = city_result['woeid']
                except Exception, e:
                    return ('ERROR', "Error fetching determining location")
                
                # yql query if we already looked up location
                yql_query = ("select * from weather.forecast where woeid={0} "
                            ).format(woeid)

            elif len(places) == 1:
                # user specified location in query, try to parse that out
                city = places[0]
                # country = None
                if len(orgs) == 1:
                    state = orgs[0]
                # if len(orgs) == 2:
                #     state = orgs[1]
                #     country = orgs[2]

                if state is not None:
                    # doing a terrible thing and assuing everything is in the US
                    state_str = "US-" + state
                    yql_query = ("select * from weather.forecast where woeid "
                                 "in (select woeid from geo.places where "
                                 "text=\"{0}\" and "
                                 "admin1.code=\"{1}\")").format(city, state_str)
                else:
                    yql_query = ("select * from weather.forecast where woeid "
                                 "in (select woeid from geo.places(1) where "
                                 "text=\"{0}\")").format(city)
            else:
                return ('ERROR',
                    "Sorry, I'm not sure where you are.")

            payload = {'q': yql_query, 'format': 'json'}
            response = requests.post(baseurl, params=payload)
            response_json = response.json()

            # try to find day
            days = set(['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday', 'tomorrow'])
            intersect = days.intersection(set(features['keywords']))

            # remember if the user asked about today/tomorrow for more natural
            # result output language
            is_today = False
            is_tomorrow = False

            if len(intersect) == 0:
                # assume the user is asking about today
                now = datetime.datetime.now()
                day = now.strftime("%A").lower()
                is_today = True
            else:
                day = intersect.pop()

            if day == 'tomorrow':
                # handle tomorrow
                now = datetime.datetime.now()
                tomorrow = now + datetime.timedelta(days=1)
                day = tomorrow.strftime("%A").lower()
                is_tomorrow = True

            yahoo_days = {"monday": "Mon", "tuesday": "Tue",
                          "wednesday": "Wed", "thursday": "Thu",
                          "friday": "Fri", "saturday": "Sat", "sunday": "Sun"}

            try:
                forecasts = response_json['query']['results']['channel']
                # 80 char line limit..
                if type(forecasts) is list:
                    # 2 ids for some reason, just take first result
                    forecasts = forecasts[0]
                forecasts = forecasts['item']['forecast']
            except Exception:
                # TODO: different response once we have an error spec up
                return ('ERROR',
                        "Error fetching weather information.")

            yahoo_day = yahoo_days[day]
            days_forecast = [f for f in forecasts if f['day'] == yahoo_day]

            # pretty format day
            day_str = ""
            if is_today:
                day_str = "today"
            elif is_tomorrow:
                day_str = "tomorrow"
            else:
                day_str = day.title()

            # format the location
            loc = ""
            if state is not None:
                loc = "{0}, {1}".format(city, state)
            else:
                loc = city

            if len(days_forecast) > 0:
                day_forecast = days_forecast[0]
            else:
                return ("Weather information not available for {0} on "
                        "{1}.".format(loc, day_str))

            # extract weather data
            high_temp = day_forecast['high']
            low_temp = day_forecast['low']
            weather_code = int(day_forecast['code'])
            weather_descript = day_forecast['text'].lower()

            preposition = ""
            if not (is_today or is_tomorrow):
                preposition = "on "

            cold_words = set(['cold', 'cool', 'freezing'])
            warm_words = set(['hot', 'warm'])
            rain_words = set(['rain', 'raining'])
            snow_words = set(['snow', 'snowing'])

            # gen responses
            response = ""
            if 'high' in tokens:
                response = ("The high for {0} in {1} will "
                            "be {2} degrees.").format(day_str, loc, high_temp)
            elif 'low' in tokens:
                response = ("The low for {0} in {1} will "
                            "be {2} degrees.").format(day_str, loc, low_temp)
            elif len(rain_words.intersection(tokens)) > 0:
                # see https://developer.yahoo.com/weather/documentation.html
                # for list of all weather condition codes
                rain_codes = set([1, 2, 3, 4, 5, 8, 9, 10, 11, 12,
                                  35, 37, 38, 39, 40, 45, 47])
                if weather_code in rain_codes:
                    response = ("It looks like there will be {0} {1}{2}."
                                ).format(weather_descript,
                                         preposition, day_str)
                else:
                    response = ("I don't see rain in the forecast {0}{1}"
                                ).format(preposition, day_str)
            elif len(snow_words.intersection(tokens)) > 0:
                snow_codes = set([5, 7, 13, 14, 15, 16, 41, 42, 43, 46])
                if weather_code in snow_codes:
                    response = ("It looks like there will be {0} {1}{2}."
                                ).format(weather_descript,
                                         preposition, day_str)
                else:
                    response = ("I don't see snow in the forecast {0}{1}."
                                ).format(preposition, day_str)
            elif len(cold_words.intersection(tokens)) > 0:
                cold_threshold = 40
                if int(low_temp) < cold_threshold:
                    response = ("It looks cold to me. Down to {0} degrees."
                                ).format(low_temp)
                else:
                    response = ("It doesn't look cold. The high will be "
                                "{0} degrees."
                                ).format(high_temp)
            elif len(warm_words.intersection(tokens)) > 0:
                warm_threshold = 69
                if int(high_temp) > warm_threshold:
                    response = ("It looks warm to me. Up to {0} degrees."
                                ).format(high_temp)
                else:
                    response = ("It doesn't look very warm. The high will be "
                                "{0} degrees."
                                ).format(high_temp)
            else:
                # some generic response
                # codes for to format like "there's going to be blank_weather..."
                there_words = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 
                                   14, 15, 16, 17, 18, 19, 21, 35, 37, 38, 39, 
                                   40, 41, 42, 43, 45, 46, 47])
                phrase_beginning = None
                if weather_descript in there_words:
                    phrase_beginning = "There's going to be"
                else:
                    phrase_beginning = "It's going to be"

                response = ("{6} {4} {5}{0} in {1}. "
                            "The high will be {2} degrees "
                            "and the low will be {3} degrees."
                            ).format(day_str, loc, high_temp,
                                     low_temp, weather_descript, 
                                     preposition, phrase_beginning)
            return response

        else:
            # no location found, get from client
            return ('NEEDS DATA - CLIENT',
                    {'location':
                        {'type': 'loc',
                         'msg': "Sorry, I can't do that without knowing where "
                                "you are. Try specifying in your question."}})

# TODO/FIXES:
# 1. Sometimes things like "Rain" and "Weather" are tagged as GPE if they
# appear first in a sentence and are capitalized
#
# 3. International locations without unique names -- given XXXXXXX, YY,
# YY is assumed to be a state which isn't always true
#
# 4. Return HTML/JSON with prettier weather info/clickable to go to full
# info on 3rd party site
#
# 5. More types of questions/more varied responses?
#
# 6. Should probably stick a Yahoo logo somewhere otherwise we're violating
# their ToS (see https://developer.yahoo.com/attribution/).
