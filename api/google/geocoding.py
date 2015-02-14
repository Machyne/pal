import requests

API_KEY = 'AIzaSyAT6m1naoO9zYBIuR_Fxbkplt1-uqR5rLk'

def geocode(location, default=None):
    url = ("https://maps.googleapis.com/maps/api/geocode/json?"
           "address={}&key={}")
    url = url.format(location.replace(' ', '+'), API_KEY)
    r = requests.get(url)
    json = r.json()
    if json['status'] != 'OK':
        return default
    results = json['results']
    if isinstance(results, list):
        results = results[0]
    loc = results['geometry']['location']
    return [loc['lat'], loc['lng']]

if __name__ == '__main__':
    print geocode('Northfield, MN', 'no response')