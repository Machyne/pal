import requests

API_KEY = 'AIzaSyAT6m1naoO9zYBIuR_Fxbkplt1-uqR5rLk'
SERVER_IP = '137.22.5.73'

def geocode(location, default=None):
    url = ("https://maps.googleapis.com/maps/api/geocode/json?"
           "address={}&key={}&userIp={}")
    url = url.format(location.replace(' ', '+'), API_KEY, SERVER_IP)
    r = requests.get(url)
    json = r.json()
    if json['status'] != 'OK':
        return default
    results = json['results']
    if isinstance(results, list):
        results = results[0]
    loc = results['geometry']['location']
    return [loc['lat'], loc['lng']]
