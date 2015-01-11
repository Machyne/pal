PRESENT_TAGS = ['VB', 'VBG', 'VBP', 'VBZ']
PAST_TAGS = ['VBD', 'VBN']


def get_tense(pos):
    present_count = len([True for x in pos if x[1] in PRESENT_TAGS])
    past_count = len([True for x in pos if x[1] in PAST_TAGS])
    return 'past' if past_count > present_count else 'present'
