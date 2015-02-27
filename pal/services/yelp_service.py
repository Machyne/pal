import random
import re

from flask import render_template

from api.yelp import yelp_api
from api.google.geocoding import geocode
from pal.services.service import Service
from pal.services.service import wrap_response


class YelpService(Service):
    _ILIKE = ['I like', 'Check out', 'Try', 'I\'m a fan of', 'Look into']

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        # Yelp has ho idea what to do with people
        for noun in params["nouns"]:
            if noun[1] == "PERSON":
                return 0
        return super(self.__class__, self).get_confidence(params)

    @wrap_response
    def go(self, params):
        features = params['features']
        location = None
        if 'location' in params.get('user-data', {}):
            location = params['user-data']['location']
        elif 'location' in params.get('client-data', {}):
            location = params['client-data']['location']
        else:
            places = [place[0] for place in features['tree'] if place[1] in
                      ['GPE', 'GSP', 'LOCATION', 'PERSON']]
            orgs = [t[0] for t in features['tree'] if t[1] == 'ORGANIZATION']
            if not len(places):
                return ('NEEDS DATA - CLIENT',
                        {'location':
                            {'type': 'loc',
                             'msg': "Sorry, I can't do that without knowing "
                                "where you are. Please specify a location or "
                                "enable location services in your browser."}})
            else:
                location = places[0]
                if len(orgs):
                    location += ', ' + orgs[0]
                location = '{},{}'.format(*geocode(location))
        nouns = features['nouns']
        nouns = filter(lambda n: (n[0].lower() not in ['me', 'i'] and
                                  n[1] not in ['GPE', 'GSP',
                                               'LOCATION', 'PERSON',
                                               'ORGANIZATION']), nouns)
        if not len(nouns):
            return ('ERROR',
                    "Sorry, I don't understand what you're looking for.")
        target = nouns[-1]
        tree = features['tree']
        if target[0] in ['find', 'me', 'some', 'i', 'local']:
            target = tree[-1]
        if target not in tree:
            return ('ERROR',
                    "Sorry, I don't understand what you're looking for.")
        index = tree.index(target)
        query = target[0]
        while index and ('JJ' in tree[index - 1][1] or
                         tree[index - 1] in nouns):
            index -= 1
            adj = tree[index][0].lower()
            if not ('near' in adj or 'close' in adj
                    or adj in ['find', 'me', 'some', 'i', 'local']):
                query = adj + ' ' + query
        businesses = yelp_api.query_api(query, location)
        results = '<ul>'
        for business in businesses:
            if 'name' not in business:
                print business
                continue
            li = '<li>'
            if 'image_url' in business:
                li += '<img src="{}"><br>'.format(business['image_url'])
            li += ('<a href="{}"><span style="font-weight: bold">{}</span>'
                   '</a><br>'.format(business['url'], business['name']))
            li += '<span>{}</span><br>'.format(business['snippet_text'])
            li += '<a href="tel:{}">{}</a>'.format(
                business['phone'], business['display_phone'])
            li += '  <span>Rating: <img src="{}"></span>'.format(
                business['rating_img_url'])
            li += '</li>'
            results += li
        lat, lng = map(float, location.split(','))
        query = "yelp find " + query
        template = render_template('yelp.html', query=query, lat=lat, lng=lng)
        template = re.sub(r'\s+', ' ', template)
        results += template
        results += '</ul>'
        # Create summary
        summary = map(lambda biz: biz['name'], businesses)
        summary[-1] = 'and ' + summary[-1]
        summary = ', '.join(summary)
        summary = '{} {}.'.format(random.choice(self._ILIKE), summary)
        return ('SUCCESS', summary, results)
