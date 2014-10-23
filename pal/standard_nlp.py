#!/usr/bin/env python
import nltk


class StandardNLP(object):
    @classmethod
    def preprocess(cls, data):
        """parses input into a usable form, applies NLP stuff"""
        tokens = nltk.word_tokenize(data)
        pos = nltk.pos_tag(tokens)
        processed_data = {'tokens': tokens, 'pos': pos}
        print processed_data
        return processed_data
