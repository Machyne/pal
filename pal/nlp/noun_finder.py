import nltk


def find_nouns(pos_tokens):
    tree = nltk.ne_chunk(pos_tokens)
    tree = [(token if isinstance(token, tuple) else
             (' '.join(map(lambda a: a[0], token.leaves())),
              token.label()))
            for token in tree]
    nouns = [token for token in tree
             if 'NN' in token[1] or ' ' in token[0]]
    return tree, nouns
