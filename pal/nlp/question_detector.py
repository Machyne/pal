def is_question(tokens):
    start_words = ['who', 'what', 'when', 'where', 'why', 'how', 'is',
                   'can', 'does', 'do']
    return tokens[0].lower() in start_words or tokens[-1] == '?'
