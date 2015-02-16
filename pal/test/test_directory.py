import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pal.feature_extractor import FeatureExtractor
from pal.standard_nlp import StandardNLP
from pal.exceptions import MissingKeyException
from pal.services.directory_service import DirectoryService

def test():
	questions = [
		"What room does Brian Charous live in?",
		"Where is Jeffrey Ondich's office?",
		"What is Brian Charous's phone number?",
		"What is Jeffrey Ondich's phone number?",
		"What is Brian Charous's email address?",
		"Email Jeffrey Ondich"]

	for question in questions:
		nlp_data = StandardNLP.process(question)
		features = FeatureExtractor.extract_features(nlp_data)
		ds = DirectoryService()
		print ds.go(features)

if __name__ == '__main__':
	test()