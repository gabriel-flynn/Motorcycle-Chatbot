import re


def is_no(text, nlp):
    _in = re.sub(r'\W+', ' ', str.lower(text))

    # Check if first word is yes or no
    first_word = _in.split(" ")[0]

    tokens = nlp(f'no {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return True


def contains_yes_or_no(text, nlp):
    _in = re.sub(r'\W+', ' ', str.lower(text))

    # Check if first word is yes or no
    first_word = _in[0]

    tokens = nlp(f'no {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return True

    tokens = nlp(f'yes {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return True


def is_yes_or_no(_in, nlp):
    _in = re.sub(r'\W+', ' ', str.lower(_in))
    word_set = set(str.lower(_in).split(" "))

    # Check if first word is yes or no
    first_word = _in.split(" ")[0]

    # Check if it's similar to yes
    tokens = nlp(f'yes {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return True

    # Check if it's similar to no
    tokens = nlp(f'no {first_word}')
    similarity = tokens[0].similarity(tokens[1])
    if similarity >= .8:
        return False

    # If first word isn't similar to yes or no then we look at the similarity of all the words in the sentence to see if something similar to yes or no was inputted
    max_yes_sim = 0
    max_no_sim = 0
    for word in word_set:
        tokens = nlp(f'yes {word}')
        tokens_no = nlp(f'no {word}')
        if len(tokens) == 2:
            y_sim = tokens[0].similarity(tokens[1])
            n_sim = tokens_no[0].similarity(tokens_no[1])
            max_yes_sim = max(y_sim, max_yes_sim)
            max_no_sim = max(n_sim, max_no_sim)
    if max_yes_sim > .8 and max_yes_sim - max_no_sim > .1:
        return True
    elif max_no_sim > .8 and max_no_sim - max_yes_sim > .1:
        return False

    # If we couldn't find a word similar to yes or no then we perform sentiment analysis to attempt to understand if their answer was more of a yes or no
    # (probably isn't very accurate but performing dependency parse or something else to get that info would be complicated and would require a lot of test cases/data)
    # With the test cases I tried on AllenNLP(https://demo.allennlp.org/sentiment-analysis/glove-sentiment-analysis) this worked really well but spaCy doesn't work quite as well with the same test cases I tried
    doc = nlp(_in)
    if doc._.sentiment.polarity >= 0.0:
        return True
    else:
        return False
