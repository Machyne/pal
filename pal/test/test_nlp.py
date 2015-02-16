import re
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pal.nlp.standard_nlp import StandardNLP
from pal.nlp.feature_extractor import FeatureExtractor

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
        os.path.join(
            os.path.dirname(__file__),
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


def test_pre_processing():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        assert processed['pos'] == tokens


def test_keywords():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        features = FeatureExtractor.extract_features(processed)
        assert features['keywords'] == exp_features['keywords']


def test_nouns():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        features = FeatureExtractor.extract_features(processed)
        assert features['nouns'] == exp_features['nouns']


def test_tense():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        features = FeatureExtractor.extract_features(processed)
        assert features['tense'] == exp_features['tense']


def test_is_question():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        features = FeatureExtractor.extract_features(processed)
        assert features['isQuestion'] == exp_features['isQuestion']


def test_question_type():
    for test in test_cases:
        sent, tokens, exp_features = test
        processed = StandardNLP.process(sent)
        features = FeatureExtractor.extract_features(processed)
        assert features['questionType'] == exp_features['questionType']

if __name__ == '__main__':
    setup()
    test_pre_processing()
    test_keywords()
    test_nouns()
    test_tense()
    test_is_question()
    test_question_type()
