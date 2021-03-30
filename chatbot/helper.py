import re


def is_no(text, nlp):
    _in = re.sub(r'\W+', ' ', str.lower(text))

    # Check if first word is yes or no
    first_word = _in[0]

    tokens = nlp(f'no {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return False
