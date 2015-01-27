#!/usr/bin/env python
# A service for translations

import requests

from pal.services.service import Service


API_URL = ("http://api.ultralingua.com/api/definitions/{from_}/{to_}/{word}"
           "?token=palrocks")


class UltraLinguaService(Service):

    _SUPPORTED_LANGUAGES = {"english", "french", "spanish",
                            "german", "portuguese", "italian"}
    _SPECIAL_ISO_CODES = {
        # these are the only 2 that aren't just the first 3
        # letters of the english name
        "french": "fra",
        "german": "deu"
    }

    default_lang = 'english'

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        pass

    @classmethod
    def _get_iso_code(cls, language):
        """ Returns the appropriate 3-letter ISO code for the
            given language.
            http://www.loc.gov/standards/iso639-2/php/code_list.php
        """
        iso = cls._SPECIAL_ISO_CODES.get(language, language[:3])
        return iso if language in cls._SUPPORTED_LANGUAGES else None

    def go(self, features):
        tokens = map(str.lower, features['tokens'])
        keywords = set(features['keywords'])
        if tokens:
            # Figure out the source and destination languages
            from_lang = self.default_lang
            to_lang = None
            languages = self._SUPPORTED_LANGUAGES.intersection(keywords)
            if len(languages):
                from_is_present = ('from' in keywords)
                to_is_present = ('to' in keywords)
                from_not_to = (from_is_present and not to_is_present)
                from_and_to = (from_is_present and to_is_present)  # NOQA
                if len(languages) == 1:
                    lang = languages.pop()
                    if from_not_to:
                        from_lang = lang
                        to_lang = self.default_lang
                    else:
                        # Only one language, the word 'from' isn't present
                        to_lang = lang
                elif len(languages) == 2:
                    # If there's 2 languages, figure out which is from_lang
                    # and which is to_lang
                    lang1 = languages.pop()
                    lang2 = languages.pop()
                    index_lang1 = tokens.index(lang1)  # NOQA
                    index_lang2 = tokens.index(lang2)  # NOQA
                    if from_is_present and to_is_present:
                        index_from = tokens.index('from')  # NOQA
                        index_to = tokens.index('to')  # NOQA

                    else:
                        # just assume that the order they appear is from->to
                        pass
                else:
                    # WTF, why are there more than 2 languages??
                    pass

            else:
                return "I'm not sure what you mean"

            # Figure out what the user wants translated
            the_word = None
            # If tokens looks like ["translate", <word>, "to", <language>],
            # assume the middle as the_word

            url = API_URL.format(from_=self._get_iso_code(from_lang),
                                 to_=self._get_iso_code(to_lang),
                                 word=the_word)
            response = requests.get(url)  # NOQA
            # parse the response from something that looks like:
            # response = [{
            #   "partofspeech": {
            #     "gender": "feminine",
            #     "number": "singular",
            #     "partofspeechcategory": "noun",
            #     "partofspeechdisplay": "noun"
            #   },
            #   "root": "chaise",
            #   "surfaceform": "chaise",
            #   "text": "chaise"
            # }, {
            #   "partofspeech": {
            #     "gender": "masculine",
            #     "number": "singular",
            #     "partofspeechcategory": "noun",
            #     "partofspeechdisplay": "noun"
            #   },
            #   "root": "fauteuil",
            #   "surfaceform": "fauteuil",
            #   "text": "fauteuil"
            # }, {
            #   "partofspeech": {
            #     "gender": "masculine",
            #     "number": "singular",
            #     "partofspeechcategory": "noun",
            #     "partofspeechdisplay": "noun"
            #   },
            #   "root": "si\u00e8ge",
            #   "surfaceform": "si\u00e8ge",
            #   "text": "si\u00e8ge"
            # }, {
            #   "clarification": ["chair a panel"],
            #   "partofspeech": {
            #     "partofspeechcategory": "verb",
            #     "partofspeechdisplay": "verb",
            #     "tense": "infinitive"
            #   },
            #   "root": "pr\u00e9sider",
            #   "surfaceform": "pr\u00e9sider",
            #   "text": "pr\u00e9sider"
            # }]

            # Return cleaned response

        return None
