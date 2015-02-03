#!/usr/bin/env python
# A service for translations

import requests

from pal.services.service import Service, wrap_response


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

    _SPECIFIER_KEYWORDS = {'from', 'to', 'in'}

    default_lang = 'english'

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    @classmethod
    def _get_iso_code(cls, language):
        """ Returns the appropriate 3-letter ISO code for the
            given language.
            http://www.loc.gov/standards/iso639-2/php/code_list.php
        """
        iso = cls._SPECIAL_ISO_CODES.get(language, language[:3])
        return iso if language in cls._SUPPORTED_LANGUAGES else None

    @staticmethod
    def _remove_quotes(tokens):
        clean_tokens = tokens
        for quote_symbol in ["\"", "'", "``", "''"]:
            (clean_tokens.remove(quote_symbol) if quote_symbol in clean_tokens
             else clean_tokens)
        return clean_tokens

    @wrap_response
    def go(self, params):
        features = params['features']
        tokens = self._remove_quotes(map(str.lower, features['tokens']))
        keywords = set(features['keywords'])

        if tokens:
            # Figure out the source and destination languages
            from_lang = None
            to_lang = None
            languages = self._SUPPORTED_LANGUAGES.intersection(keywords)

            def get_lang_after(keyword, default=self.default_lang):
                is_present = (keyword in keywords)
                next_word = (tokens[tokens.index(keyword)+1] if is_present
                             else None)
                lang = (next_word if is_present and next_word in languages
                        else default)
                return lang
            if len(languages):

                from_lang = get_lang_after('from')
                to_lang = get_lang_after('to')
                nondefault_langs = languages.difference({self.default_lang})
                if (from_lang == self.default_lang
                        and to_lang == self.default_lang
                        and len(nondefault_langs) > 0):
                    # language(s) specified without "from" or "to" keywords
                    if len(nondefault_langs) == 1:
                        to_lang = nondefault_langs.pop()
                    elif 'in' in keywords:
                        # ex: "What's German in Spanish?"
                        to_lang = get_lang_after('in')
                    else:
                        return ('ERROR', "I can't tell what languages you want"
                                         " to translate between.")
            else:
                return 'ERROR', "I'm not sure what you mean."

            # Figure out what the user wants translated
            the_word = None
            # If tokens looks like ["translate", <word>, "to", <language>],
            # assume the middle as the_word
            specifiers = self._SPECIFIER_KEYWORDS.intersection(keywords)
            for keyword in specifiers:
                word_before = tokens[tokens.index(keyword)-1]
                if word_before not in [from_lang, to_lang]:
                    the_word = word_before
                    break
            if the_word is None:
                return ('ERROR', "I can't figure out what word you want "
                                 "translated.")

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
