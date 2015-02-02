# coding = utf-8
"""
Yelp API v2.0 code sample.

This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Docs: http://www.yelp.com/developers/documentation for the API documentation.


Sample usage of the program:
`python yelp_api.py --term="bars" --location="San Francisco, CA"`
`python yelp_api.py --term="food" --location="37.788022,-122.399797"`
"""
import argparse
import json
import pprint
import re
import sys
import urllib
import urllib2

import oauth2


API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'Northfield, MN'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

CONSUMER_KEY = 'yCvKVXaC0lZSvCFDkwzvrg'
CONSUMER_SECRET = 'MNOC-nytnZiXoIFicf16NJweS2Q'
TOKEN = '-dDJM7fYdCBinzn4eOX8OVx4Ip-6tPxF'
TOKEN_SECRET = 'fe5f8pXgFtGo1BjahpkW2EEeKoI'

is_main = __name__ == '__main__'


def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, path)

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(
        method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                               consumer, token)
    signed_url = oauth_request.to_url()
    
    if is_main:
        print 'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    if re.match(r'[0-9.-]+', location):
        url_params['ll'] = location
    else:
        url_params['location'] = location.replace(' ', '+')
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(term, location)

    businesses = response.get('businesses')

    if not businesses:
        if is_main:
            print 'No businesses for {0} in {1} found.'.format(term, location)
        return

    if is_main:
        print ('{0} businesses found, querying business info for the top '
               'result "{1}"...'.format(len(businesses), businesses[0]['id']))

    responses = map(lambda biz: get_business(biz['id']), businesses)

    if is_main:
        print 'Result for business "{0}" found:'.format(businesses[0]['id'])
        pprint.pprint(businesses[0], indent=2)
        pprint.pprint(responses[0], indent=2)

    return responses


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-q', '--term', dest='term', default=DEFAULT_TERM,
        type=str, help='Search term (default: %(default)s)')

    parser.add_argument(
        '-l', '--location', dest='location',
        default=DEFAULT_LOCATION, type=str,
        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except urllib2.HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0}. Abort program.'.format(error.code))


if is_main:
    main()
