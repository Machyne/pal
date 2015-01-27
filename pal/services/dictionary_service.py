# A service for definitions and synonyms

from bs4 import BeautifulSoup
import requests

from pal.services.service import Service, response_codes, wrap_response


class DictionaryService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    _SYNONYM = set(['synonyms', 'synonym', 'similar', 'same'])

    _ANTONYM = set(['antonyms', 'antonym', 'opposite'])

    @wrap_response
    def go(self, features):
        tokens = map(str.lower, features['tokens'])
        while len(tokens) and (len(tokens[-1]) < 3 or
                               tokens[-1] == 'mean'):
            # Assume last real word that isn't 'mean' is our target.
            tokens = tokens[:-1]
        if len(tokens):
            word = tokens[-1]
            tokens = set(tokens[:-1])
            synonym = bool(len(self._SYNONYM.intersection(tokens)))
            antonym = bool(len(self._ANTONYM.intersection(tokens)))
            if synonym or antonym:
                lead = '{} for "{}": '.format(
                    'Synonyms' if synonym else 'Antonyms', word)
                try:
                    # These are different url than the definitions.
                    url = 'http://www.thesaurus.com/browse/' + word
                    r = requests.get(url)
                    soup = BeautifulSoup(r.text)
                    wrapper = soup.find('div', class_='synonyms')

                    if synonym:
                        wrapper = wrapper.find(class_='relevancy-list')
                    else:
                        wrapper = wrapper.find('section', class_='antonyms')

                    # Conveniently tagged with class="text" in both cases.
                    all_words = wrapper.find_all('span', class_='text')
                    all_words = map(lambda el: el.get_text(), all_words)
                    # Summary will be up to 7, data will be all of them.
                    return (response_codes.SUCCESS,
                            lead + ', '.join(all_words[:7]) + '.',
                            lead + ', '.join(all_words) + '.')
                except Exception:
                    things = 'synonyms' if synonym else 'antonyms'
                    return (response_codes.ERROR,
                            'I couldn\'t find any ' + things +
                            ' for ' + word + '.')
            else:
                try:
                    url = 'http://dictionary.reference.com/browse/' + word
                    r = requests.get(url)
                    soup = BeautifulSoup(r.text)
                    # The summary will just be the first definition.
                    first_def = soup.find_all(class_='def-content')
                    first_def = first_def[0].get_text()
                    short = 'Definition of "{}": {}'.format(word, first_def)
                    # The data will be everything.
                    full_text = ''
                    for def_list in soup.find_all(class_='def-list'):
                        full_text += def_list.get_text()
                    return (response_codes.SUCCESS, short, full_text)
                except Exception:
                    return (response_codes.ERROR,
                            'I couldn\'t find any definitions for ' + word +
                            '.')
        return None
