import random
import re

import sqlite3
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from helper import is_no


class Chatbot:
    def __init__(self, user_data):
        self.nlp = spacy.load("en_core_web_md")
        self.user_data = user_data
        self.name = ""
        self.conn = sqlite3.connect("knowledge_base.db").cursor()

    # Controls the flow of the chatbot
    def start(self):
        if not self.user_data:
            self.name = self.get_name()
            is_new_motorcycles = self.greet_user()
            if is_new_motorcycles:
                self.provide_info_on_motorcycles()
            else:
                pass

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

        # Check if it's similar to yes
        tokens = self.nlp(f'yes {first_word}')
        similarity = tokens[0].similarity(tokens[1])
        if similarity >= .8:
            return True

        # Check if it's similar to no
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

    # TODO: current approach for generating the SQL query is pretty naive - a dependency parse would work better
    def provide_info_on_motorcycles(self):
        print("Motorcycling is one of my favorite things to do (or at least pretend to do, I am a bot after all)! To provide some background: a motorcycle is also commonly referred to as a motorbike, bike, or cycle and it is a two- or three-wheeled motor vehicle (although I think three-wheeled motor vehicles being motorcycles is debatable)."
              "Motorcycle design varies greatly to suit a range of different purposes: long-distance travel, commuting, cruising, sport, including racing, and off-road riding."
              "Motorcycling is riding a motorcycle and being involved in other related social activity such as joining a motorcycle club and attending motorcycle rallies.")

        print("\nSorry for all that information! Hopefully that helped and here's two fun facts about motorcycles: ")

        # Print two facts instead of one? Some of the results from this query still aren't great even with a lot of the junk ones removed
        self.conn.execute(
            "select sentence FROM data where term == 'motorcycle' and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' ")
        rows = self.conn.fetchall()
        facts = random.sample(rows, 2)
        for i, fact in enumerate(facts, start=1):
            print(f'{i}. {fact[0]}')

        question = input("\nDo you have any questions? Feel free to ask me things like 'How can I get a license?', 'What was the first motorcycle?',  'Tell me about licenses', etc. I'll do my best to answer it!\nIf not just say no and we'll move onto the next step!\n")
        if is_no(question, self.nlp):
            return
        else:
            doc =self.nlp(question)
            query = ""
            while not query:
                last_adj = []
                for indx, token in enumerate(doc):
                    if token.pos_ == "NOUN":
                        if last_adj and last_adj[1] == indx-1:
                            query += last_adj[0].text + " "
                        query += token.lemma_ # Get the lemma of the word - helps for plurals like licenses, motorcycles, etc. where we may not be able to find licenses but we can find license
                        break
                    elif token.pos_ == "ADJ":
                        last_adj = [token, indx]
                if not query:
                    input("I don't think that was a valid question or command, please try another question")
            self.conn.execute(
                f"select sentence FROM data where sentence like '%{query}%' and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' ")
            rows = self.conn.fetchall()
            if not rows:
                print(f"I couldn't find anything that matched {query} exactly. I'll try another method")
            print(query)
            new_query = ""
            for indx, q in enumerate(query.split(" ")):
                if indx == 0:
                    new_query = f"where sentence like '%{q}%' "
                else:
                    new_query += f"and sentence like '%{q}%'"

            self.conn.execute(
                f"select sentence FROM data {new_query} and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' ")
            rows = self.conn.fetchall()
            if not rows:
                print(f"Even with the 2nd method I couldn't find anything, sorry about that! We'll move onto something else")
            else:
                print(f"\nI found {len(rows)} result{'s' if len(rows) >= 2 else ''}, here's {2 if len(rows) >= 2 else 'the result'}:")
                if len(rows) >= 2:
                    results = random.sample(rows, 2)
                else:
                    results = rows

                for indx, r in enumerate(results, start=1):
                    print(f'{indx}. {r[0]}')

                print("Hopefully that answered your question! If not you'll have an opportunity to ask me more questions later")
