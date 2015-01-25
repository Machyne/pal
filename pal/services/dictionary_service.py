# A service for definitions and synonyms

from bs4 import BeautifulSoup
import requests

from pal.services.service import Service


class DictionaryService(Service):
    name = 'dictionary'

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    _SYNONYM = set(['synonyms', 'synonym', 'similar', 'same'])

    _ANTONYM = set(['antonyms', 'antonym', 'opposite'])

    def go(self, features):
        tokens = map(str.lower, features['tokens'])
        while len(tokens) and (len(tokens[-1]) < 3 or
                               tokens[-1] == 'mean'):
            # Assume last real word that isn't 'mean' is our target.
            tokens = tokens[:-1]
        if len(tokens):
            word = tokens[-1]
            tokens = set(tokens)
            synonym = bool(len(self._SYNONYM.intersection(tokens)))
            antonym = bool(len(self._ANTONYM.intersection(tokens)))
            if synonym or antonym:
                # These are different url than the definitions.
                url = 'http://www.thesaurus.com/browse/' + word
                r = requests.get(url)
                soup = BeautifulSoup(r.text)
                big_wrapper = soup.find('div', class_='synonyms')

                wrapper = None
                if synonym:
                    wrapper = big_wrapper.find(class_='relevancy-list')
                else:
                    wrapper = big_wrapper.find('section', class_='antonyms')

                # Conveniently tagged with class="text" in both cases.
                all_words = wrapper.find_all('span', class_='text')
                all_words = map(lambda el: el.get_text(), all_words)
                lead = '{} for "{}": '.format(
                    'Synonyms' if synonym else 'Antonyms', word)
                # Summary will be up to 7, body will be all of them.
                return {'response': lead + ', '.join(all_words[:7]) + '.',
                        'body': lead + ', '.join(all_words) + '.'}
            else:
                url = 'http://dictionary.reference.com/browse/' + word
                r = requests.get(url)
                soup = BeautifulSoup(r.text)
                # The summary will just be the first definition.
                first_def = soup.find_all(class_='def-content')[0].get_text()
                short = 'Definition of "{}": {}'.format(word, first_def)
                # The body will be everything.
                full_text = ''
                for def_list in soup.find_all(class_='def-list'):
                    full_text += def_list.get_text()
                return {'response': short, 'body': full_text}
        return None
