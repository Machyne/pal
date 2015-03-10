#!/usr/bin/env python
#
# Taken from:
# http://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-
#                                           words-to-integers-python

import re

numwords = {}


def text_to_int(textnum):
    if not numwords:
        units = ['zero', 'one', 'two', 'three', 'four', 'five', 'six',
            'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
            'eighteen', 'nineteen']

        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 
            'seventy', 'eighty', 'ninety']

        scales = ['hundred', 'thousand', 'million', 'billion', 'trillion', 
            'quadrillion', 'quintillion', 'sexillion', 'septillion', 
            'octillion', 'nonillion', 'decillion' ]

        numwords['and'] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8,
        'ninth':9, 'twelfth':12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]
    current = result = 0
    tokens = re.split(r'[\s-]+', textnum)
    for word in tokens:
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = '%s%s' % (word[:-len(ending)], replacement)

            if word not in numwords:
                raise Exception('Illegal word: ' + word)

            scale, increment = numwords[word]

        if scale > 1:
            current = max(1, current)

        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

if __name__ == '__main__':
    print text_to_int('one hundred seven')
    print text_to_int('twelve')
    print text_to_int('eight million')
    print text_to_int('forty-five')
