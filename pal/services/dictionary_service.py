import re

from bs4 import BeautifulSoup
import requests

from pal.services.service import Service


class DictionaryService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    _SYNONYM = set(['synonym', 'similar', 'same'])

    _ANTONYM = set(['antonym', 'opposite'])

    def go(self, features):
        print 'dict go'
        tokens = map(str.lower, features['tokens'])
        while len(tokens) and (len(tokens[-1]) < 3 or
                               tokens[-1] == 'mean'):
            tokens = tokens[:-1]
        if len(tokens):
            word = tokens[-1]
            tokens = set(tokens)
            if len(self._SYNONYM.intersection(tokens)):
                print 'syno'
            elif len(self._ANTONYM.intersection(tokens)):
                print 'anto'
            else:
                url = 'http://dictionary.reference.com/browse/' + word
                r = requests.get(url)
                soup = BeautifulSoup(r.text)
                full_text = ''
                short = soup.find_all(class_='def-content')[0].get_text()
                for def_list in soup.find_all(class_='def-list'):
                    full_text += def_list.get_text()
                return {'response': short, 'body': full_text}
