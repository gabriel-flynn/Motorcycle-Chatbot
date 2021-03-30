import random

import sqlite3
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from motorcycle_finder import MotorcycleFinder
from helpers import is_no, is_yes_or_no


class Chatbot:
    def __init__(self, user_data):
        self.nlp = spacy.load("en_core_web_md")

        # For NER (at least for detecting a person's name) it seems to perform a lot better with small, it wouldn't detect my name on medium
        self.ner = spacy.load("en_core_web_sm")
        self.user_data = user_data
        self.name = ""
        self.conn = sqlite3.connect("knowledge_base.db").cursor()
        self.motorcycle_finder = MotorcycleFinder(ner=self.ner)

    # Controls the flow of the chatbot
    def start(self):
        if not self.user_data:
            # self.name = self.get_name()
            # is_new_motorcycles = self.greet_user()
            # if is_new_motorcycles:
            #     self.provide_info_on_motorcycles()
            # else:
            #     print("That's awesome that you're already familiar with motorcycling!")
            # self.prompt_user_if_they_want_overview_of_motorcycle_categories()
            self.motorcycle_finder.begin_questions()

    def get_name(self):
        greeting = "Hi, I'm Moto and I'm a chatbot that is very knowledgeable about motorcycles! " \
                   "I'd love to introduce you to the world of motorcycles and help find the perfect bike for you, what is your name?\n" \
                   "I can understand sentences so feel free to talk to me just like how you'd talk to another person!\n"
        try_again = "Sorry I didn't catch that, can you please tell me your name again?\n"
        iteration = 0
        name = None
        while not name:
            _in = input(greeting if iteration == 0 else try_again)
            doc = self.ner(_in)
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
        return is_yes_or_no(_in, self.nlp)

    # TODO: current approach for generating the SQL query is pretty naive - a dependency parse would work better
    def provide_info_on_motorcycles(self):
        print(
            "Motorcycling is one of my favorite things to do (or at least pretend to do, I am a bot after all)! "
            "\nTo provide some background: a motorcycle is also commonly referred to as a motorbike, bike, or cycle and it is a two- or three-wheeled motor vehicle (although I think three-wheeled motor vehicles being called motorcycles is debatable)."
            "\nMotorcycle design varies greatly to suit a range of different purposes: long-distance travel, commuting, cruising, sport, including racing, and off-road riding."
            "\nMotorcycling is riding a motorcycle and can involve other related social activity such as joining a motorcycle club, attending motorcycle rallies and going on group rides with friends or strangers.")

        print("\nSorry for all that information! Hopefully that helped and here's two fun facts about motorcycles: ")

        # Print two facts instead of one? Some of the results from this query still aren't great even with a lot of the junk ones removed
        self.conn.execute(
            "select sentence FROM data where term == 'motorcycle' and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' ")
        rows = self.conn.fetchall()
        facts = random.sample(rows, 2)
        for i, fact in enumerate(facts, start=1):
            print(f'{i}. {fact[0]}')

        question = input(
            "\nDo you have any questions? Feel free to ask me things like 'How can I get a license?', 'What was the first motorcycle?',  'Tell me about licenses', etc. I'll do my best to answer it!\nIf not just say no and we'll move onto the next step!\n")
        if is_no(question, self.nlp):
            return
        else:
            doc = self.nlp(question)
            query = ""
            while not query:
                last_adj = []
                for indx, token in enumerate(doc):
                    if token.pos_ == "NOUN":
                        if last_adj and last_adj[1] == indx - 1:
                            query += last_adj[0].text + " "
                        query += token.lemma_  # Get the lemma of the word - helps for plurals like licenses, motorcycles, etc. where we may not be able to find licenses but we can find license
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
                print(
                    f"Even with the 2nd method I couldn't find anything, sorry about that! We'll move onto something else")
            else:
                print(
                    f"\nI found {len(rows)} result{'s' if len(rows) >= 2 else ''}, here's {2 if len(rows) >= 2 else 'the result'}:")
                if len(rows) >= 2:
                    results = random.sample(rows, 2)
                else:
                    results = rows

                for indx, r in enumerate(results, start=1):
                    print(f'{indx}. {r[0]}')

                print(
                    "Hopefully that answered your question! If not you'll have an opportunity to ask me more questions later")

    def prompt_user_if_they_want_overview_of_motorcycle_categories(self):
        _in = input(
            "\nWould you like an overview of the different types of motorcycles? I'll explain the differences between Sport bikes, cruisers, naked bikes, etc.\n")
        yes = is_yes_or_no(_in, self.nlp)
        if yes:
            print("\n\nSport bikes are high horsepower bikes designed for the race track. "
                  "The seating position is very aggressive and they typically aren't the best for commuting but they are the best at cornering."
                  "\nCrusiers tend to be one of the comfier bikes to ride and are great at 'crusing'. They make good commuter bikes but tend to a lack in cornering ability compared to sport bikes, naked bikes, etc."
                  "\nNaked bikes are, as the name implies, a little more naked when compared to sport bikes. They have very little fairings (body panels on a motorcycle), tend to have a lot of torque, and are usually much more comfortable than sport bikes as the seating position is more upright rather than hunched over"
                  "\nAdventure bikes are great for long distance rides as they tend to have lots of aftermarket parts available to add storage space, they are a lot taller than other bikes, and they handle trails really well. You can think of an adventure bike as a more practical or more steet-capable version of dirt bikes in a sense (geared better for the city, bigger engine, etc."
                  "\nDirt bikes are amazing off-road bikes as the name implies but aren't necessarily the best for the street as they usually aren't able to achieve very high top speeds as they're made for off-road and they also tend to have a much more frequent maintenance schedule. Dual-sport bikes would be a good option to look for if you want to do a pretty equal amount of off-road and street riding")
        else:
            print("Ok, we'll go ahead and move onto the questions to help you find the perfect motorcycle for you!")
