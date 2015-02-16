#!/usr/bin/env python
# coding: utf-8
#
# Test the heuristics/classification of queries
#
# Author: Alex Simonides

from pal.classifier import StandardNLP, FeatureExtractor, Classifier
from pal.test import parse_examples
from pal.test.case import PALTestCase


class HeuristicTestCase(PALTestCase):

    def __init__(self):
        self.examples = parse_examples()
        super(HeuristicTestCase, self).__init__()

    def test_classifier(self):
        """ Runs through the example queries and tests that they get
            classified correctly
        """
        for service, queries in self.examples.iteritems():
            for query in queries:
                yield self._check_query, query, service

    @staticmethod
    def _check_query(query, expected_service):
        """ Asserts that a given query is classified to the given service."""
        params = {
            'query': query,
            'client': "web"
        }
        StandardNLP.process(params)
        FeatureExtractor.process(params)
        Classifier.process(params)
        assert params['service'] == expected_service, (
            "The query \"{}\" is supposed to go to the {} service"
            ", but went to {} instead.".format(query, expected_service,
                                               params['service']))

if __name__ == "__main__":
    import nose
    nose.runmodule()
