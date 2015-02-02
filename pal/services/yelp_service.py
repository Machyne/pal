from api.yelp import yelp_api
from pal.services.service import Service
from pal.services.service import wrap_response


class YelpService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @wrap_response
    def go(self, params):
        if 'location' not in params.get('user-data', {}):
            return ('NEEDS MORE',
                {'location':
                    {'type': 'loc',
                     'default': [44.46126762422732, -93.15553424445801]}})
        try:
            lat, lon = map(float, params['user-data']['location'].split(','))
        except Exception:
            return ('ERROR', "I can't handle that format of location data.")
        nouns = params['features']['nouns']
        nouns = filter(lambda n: n not in ['me', 'i', 'I'], nouns)
        target = nouns[-1]
        tree = params['features']['tree']
        if target not in tree:
            return ('ERROR',
                    "Sorry, I don't understand what you're looking for.")
        index = tree.index(target)
        query = target[0]
        while index and ('JJ' in tree[index - 1][1] or
                         tree[index - 1] in nouns):
            index -= 1
            adj = tree[index][0]
            if 'near' in adj or 'close' in adj:
                continue
            query = tree[index][0] + ' ' + query
        businesses = yelp_api.query_api(query, '{},{}'.format(lat, lon))
        results = '<ul>'
        for business in businesses:
            li = '<li>'
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
        results += '</ul>'
        return results
