#!/usr/bin/env python
import nltk


class FeatureExtractor(object):
    @classmethod
    def extractFeatures(cls, processed_data):
        """Does semantic analysis stuff, extracts important information
        to NLP'd data.
        """
        tree = nltk.ne_chunk(processed_data['pos'])
        tree = [(token if isinstance(token, tuple) else
                 (' '.join(map(lambda a: a[0], token.leaves())),
                  token.label()))
                for token in tree]
        nouns = [token for token in tree
                 if 'NN' in token[1] or ' ' in token[0]]
        features = {'keywords': ['movie'],
                    'nouns': nouns,
                    'tense': 'past',
                    'isQuestion': True,
                    'questionType': 'quantity'}
        return features
