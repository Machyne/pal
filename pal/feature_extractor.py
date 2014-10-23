#!/usr/bin/env python
class FeatureExtractor(object):
    @classmethod
    def extractFeatures(cls, processed_data):
        """Does semantic analysis stuff, extracts important information
        to NLP'd data.
        """
        nouns = [w[0] for w in processed_data['pos'] if 'NN' in w[1]]
        print nouns
        features = {'keywords': ['movie'],
                    'nouns': [('person', 'Tom Hanks')],
                    'tense': 'past',
                    'isQuestion': True,
                    'questionType': 'quantity'}
        return features
