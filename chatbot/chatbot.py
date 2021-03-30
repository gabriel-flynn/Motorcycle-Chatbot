import re

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob


class Chatbot:
    def __init__(self, user_data):
        self.nlp = spacy.load("en_core_web_md")
        self.user_data = user_data
        self.name = ""

    def start(self):
        if not self.user_data:
            self.name = self.get_name()
            self.greet_user()

    def get_name(self):
        greeting = "Hi, I'm Moto and I'm a chatbot that is very knowledgeable about motorcycles! " \
                   "I'd love to introduce you to the world of motorcycles and help find the perfect bike for you, what is your name?\n" \
                   "I can understand sentences so feel free to talk to me just like how you'd talk to another person!\n"
        try_again = "Sorry I didn't catch that, can you please tell me your name again?\n"
        iteration = 0
        name = None
        while not name:
            _in = input(greeting if iteration == 0 else try_again)
            doc = self.nlp(_in)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text
            iteration += 1
            if len(_in.split(" ")) == 1:
                name = _in
        return name

    # Return true - new to motorcycles or false - familiar with motorcycles
    def greet_user(self):

        # Setup for sentiment analysis (if needed)
        spacy_text_blob = SpacyTextBlob()
        self.nlp.add_pipe(spacy_text_blob)

        # Greet the user and get their response
        greeting = f"Hey {self.name}, it's nice to meet you! Are you new to motorcycles?\n"
        _in = input(greeting)
        _in = re.sub(r'\W+', ' ', str.lower(_in))
        word_set = set(str.lower(_in).split(" "))

        # Check if first word is yes or no
        first_word = _in[0]

        if first_word == 'yes':
            tokens = self.nlp(f'yes {first_word}')
            similarity = tokens[0].similarity(tokens[1])
            if similarity >= .8:
                return True
        elif first_word == 'no':
            tokens = self.nlp(f'no {first_word}')
            similarity = tokens[0].similarity(tokens[1])
            if similarity >= .8:
                return False

        # If first word isn't similar to yes or no then we look at the similarity of all the words in the sentence to see if something similar to yes or no was inputted
        max_yes_sim = 0
        max_no_sim = 0
        for word in word_set:
            tokens = self.nlp(f'yes {word}')
            tokens_no = self.nlp(f'no {word}')
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
        doc = self.nlp(_in)
        if doc._.sentiment.polarity >= 0.0:
            return True
        else:
            return False
