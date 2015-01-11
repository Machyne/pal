import re
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pal.standard_nlp import StandardNLP
from pal.feature_extractor import FeatureExtractor

keywords = 'keywords'
nouns = 'nouns'
tense = 'tense'
isQuestion = 'isQuestion'
questionType = 'questionType'
actionType = 'actionType'
true = True
false = False

test_cases = []


def setup():
    examples_file = os.path.abspath(
        os.path.join(os.path.dirname( __file__ ),
        '..', 'examples', 'nlp_features.md'))
    with open(examples_file) as f:
        sentences = re.findall(r'\*\*[^}]+\}', f.read())
        for sent in sentences:
            parts = map(
                lambda s: re.sub(r'\s+', ' ', s.strip()),
                re.split(r'\n *\n', sent))
            parts[0] = parts[0][2:-2]
            parts = map(eval, parts)
            test_cases.append(tuple(parts))


def test_example_cases():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        assert processed['pos'] == tokens
        features = FeatureExtractor.extract_features(processed)
        print sent, features['questionType']
        # assert features == exp_features

if __name__ == '__main__':
    setup()
    test_example_cases()