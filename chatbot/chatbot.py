import json
import random

import sqlite3
import time

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from motorcycle_finder import MotorcycleFinder
from helpers import is_no, is_yes_or_no, contains_yes_or_no
from botapi.User import create_user_and_get_user_location, update_location, get_closest_track_travel_time, \
    save_motorcycle_recommendations
from sentence_transformers import SentenceTransformer, util


class Chatbot:
    def __init__(self, name="", motorcycles=[], closest_track=None, **kwargs):
        print("Loading in NLP models...")
        self.nlp = spacy.load("en_core_web_md")

        # For NER (at least for detecting a person's name) it seems to perform a lot better with small, it wouldn't detect my name on medium
        self.ner = spacy.load("en_core_web_sm")

        # user data
        self.name = name
        self.motorcycles = motorcycles
        self.closest_track = closest_track
        self.conn = sqlite3.connect("knowledge_base.db").cursor()
        self.motorcycle_finder = MotorcycleFinder(ner=self.ner)
        self.sbert_model = SentenceTransformer('stsb-roberta-base')
        self.new_user = False if name else True  # will eventually be something like True if name else False

    # Controls the flow of the chatbot
    def start(self):
        if not self.new_user:
            self.new_user = self.get_continue_session_or_restart()

        wants_to_search = False
        if self.new_user:
            self.name = self.get_name()
            is_new_motorcycles = self.greet_user()
            if is_new_motorcycles:
                self.provide_info_on_motorcycles()
            else:
                print("That's awesome that you're already familiar with motorcycling!")
        else:
            wants_to_search = self.get_user_wants_to_search_again()
        if self.new_user or wants_to_search:
            self.prompt_user_if_they_want_overview_of_motorcycle_categories()
            self.motorcycles = self.motorcycle_finder.begin_questions()
            self.get_location()
            save_motorcycle_recommendations(self.motorcycles)
        self.allow_user_to_ask_questions()
        self.thank_user_for_their_time()

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
            "\nTo provide some background: a motorcycle is also commonly referred to as a motorbike, bike, or cycle and it is a two- or three-wheeled motor vehicle (although I think three-wheeled motor vehicle being one is debatable)."
            "\nMotorcycle design varies greatly to suit a range of different purposes: long-distance travel, commuting, cruising, sport, and off-road riding."
            "\nMotorcycling is riding a motorcycle and can involve other related social activity such as joining a motorcycle club, attending motorcycle rallies and going on group rides with friends or strangers.")

        print("\nSorry for all that information! Hopefully that helped and here's two fun facts about motorcycles: ")

        # Print two facts instead of one? Some of the results from this query still aren't great even with a lot of the junk ones removed
        self.conn.execute(
            "select sentence FROM data where term == 'motorcycle' and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' and sentence not like '%Wikipedia%' ORDER BY RANDOM() LIMIT 2")
        facts = self.conn.fetchall()
        for i, fact in enumerate(facts, start=1):
            print(f'{i}. {fact[0]}')

        question = input(
            "\nDo you have any questions? Feel free to ask me things like 'How can I get a license?', 'What was the first motorcycle?',  'Tell me about licenses', etc. I'll do my best to answer it!\nIf not just say no and we'll move onto the next step!\n")
        if is_no(question, self.nlp):
            return
        else:
            self.ask_question(question)
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

    def get_location(self):
        response = create_user_and_get_user_location(self.new_user, self.name)
        location_string = response['location']['location_string']

        print(location_string)
        if location_string:
            location_message = f"I have detected you as being located near {location_string} is that correct?"
        else:
            location_message = "I was unable to detect your location, where are you located?" \
                               "\nPlease enter either a location near to where you're located:" \
                               "\nExamples: 'Texas', 'Dallas, Texas', 'United States', etc."

        # Encourage user to attend a track day and confirm their location
        _in = input(
            "I hope that information helped you in the search for your next motorcycle! While motorcycling definitely isn't the safest hobby, it's one of my favorites!\n"
            "I highly encourage you to attend a track day at your local motorcycle track as it's a great way to improve as well as being a great opportunity to push your new bike to it's limits!"
            f"\n\n{location_message}\n")

        no = False
        if contains_yes_or_no(_in, self.nlp):
            if not is_yes_or_no(_in, self.nlp):
                no = True
                _in = input("Please enter either a location near to where you're located:"
                            "\nExamples: 'Texas', 'Dallas, Texas', 'United States', etc.")

        if not location_string or no:
            location = ""
            while not location:
                doc = self.nlp(_in)
                for token in doc.ents:
                    if token.label_ == "GPE" or token.label_ == "ORG":  # Sometimes city gets detected as an ORG
                        location += f'{", " if location else ""}{token.text}'
                if location:
                    break
                _in = input(
                    "I didn't quite a catch your location, please input something like 'Texas' 'Dallas, Texas', 'United States', 'UT Dallas' etc.")
            update_location(location)
        print("Finding travel time to the nearest track...\n")
        response = get_closest_track_travel_time()
        travel_time = response['travel_time']
        closest_track = response['track']
        website = ""
        if closest_track['url']:
            website = f"\nHere's a link to their website to found out more information: {closest_track['url']}"
        print(
            f"The nearest motorcycle track is {travel_time} away from you! It's called {closest_track['name']} and it's located at {closest_track['address']}. {website}")

    # Returns false if they want to continue with previous session data, true if they want to start over
    def get_continue_session_or_restart(self):
        _in = input(f"Hey it's Moto here again and I'm super happy to get the change to talk to you again!"
                    f"\nAm I speaking to {self.name}? If you're not {self.name} or you'd like to meet me all over again just tell me you want to start over or that it's not you\n")

        # Perform semantic textual similarity using SentenceTransformer
        no_sentences = ["No, I want to start over", "No, that's not me", "I want to meet all over again",
                        "Let's start over", f"No I'm not {self.name}"]
        yes_sentences = [f"Yes I'm {self.name}", f"Yes, you got the right person", "I don't want to start over",
                         "Yes that's me"]
        return self.compute_if_first_sentences_has_higher_cosine_similarity(_in, no_sentences,
                                                                            yes_sentences)  # Returns true if the first _sentences argument is True

    def get_user_wants_to_search_again(self):
        # TODO: Handle case where they had no motorcycles suggested to them (none matched their criteria)
        _in = input(
            f"Thanks for clearing that up {self.name}! I had a ton of fun last time finding new bike recommendations for you such as the {self.motorcycles[0]['make']} {self.motorcycles[0]['model']} I told you about last time!\n"
            f"\nDon't worry, I won't be mad if you go with something else but make sure you don't forget to visit the track I told you about earlier {self.closest_track['name']} if you get the change, you won't regret it!"
            "\n\nEnough about that, would you like to search for another motorcycle? If not I'm happy to provide you with some interesting facts and answer your questions!\n")

        yes_sentences = ["Yes, that sounds great", "Yes, I would love more recommendations",
                         "Sure, let's search for more motorcycles"]
        no_sentences = ["No, I'm good for now", "No, I'd rather hear some interesting facts", "Nah, I'd rather not"]
        return self.compute_if_first_sentences_has_higher_cosine_similarity(_in, yes_sentences, no_sentences)

    # Return true if sentences1 has the highest similarity score and false if sentences2 has the highest
    def compute_if_first_sentences_has_higher_cosine_similarity(self, _in, sentences1, sentences2):
        # Perform semantic textual similarity using SentenceTransformer
        _input = [_in]

        max_one = self.compute_highest_cosine_similarity(sentences1, _input)
        max_two = self.compute_highest_cosine_similarity(sentences2, _input)
        return True if max_one > max_two else False

    def compute_highest_cosine_similarity(self, sentences, _input):
        embeddings = self.sbert_model.encode(sentences, convert_to_tensor=True)
        answer_embedding = self.sbert_model.encode(_input, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embeddings, answer_embedding)
        _max = 0
        for i in range(len(sentences)):
            # print("{} \t\t {} \t\t Score: {:.4f}".format(sentences[i], _input, cosine_scores[i][0]))
            _max = max(_max, cosine_scores[i][0])
        return _max

    def ask_question(self, initial_input):
        doc = self.nlp(initial_input)
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
                query = input("I don't think that was a valid question or command, please try another question")
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
                f"\nI found {len(rows)} result{'s' if len(rows) >= 2 else ''} for, here's {'2 of them' if len(rows) >= 2 else 'the result'}:")
            if len(rows) >= 2:
                results = random.sample(rows, 2)
            else:
                results = rows

            for indx, r in enumerate(results, start=1):
                print(f'{indx}. {r[0]}')

    def allow_user_to_ask_questions(self):
        _in = input(
            "Awesome! I love sharing the facts I know! To start tell me if you want to hear a random fact or if you have a question.\n")
        random_fact = ["I want to hear a random fact", "Tell me a random fact"]
        question = ["I have a question", "Can I ask you something?", "Let me ask you a question"]

        # If random fact
        if self.compute_if_first_sentences_has_higher_cosine_similarity(_in, random_fact, question):
            fact_queries = ['racing', 'sport', 'road', 'engine', 'motorcycle']
            while True:
                for i in range(3):
                    term = random.sample(fact_queries, 1)[0]
                    # Print two facts instead of one? Some of the results from this query still aren't great even with a lot of the junk ones removed
                    print(f"\nFetching two facts under the term {term}")
                    self.conn.execute(
                        f"select sentence FROM data where term == '{term}' and sentence not like '%[%' and sentence not like '%ISBN%' and sentence not like '%^ %' and sentence not like '%Wikipedia%' ORDER BY RANDOM() LIMIT 2")
                    facts = self.conn.fetchall()
                    for i, fact in enumerate(facts, start=1):
                        print(f'{i}. {fact[0]}')
                    print()
                    time.sleep(5)
                _in = input("Would you like more facts or would you like to ask questions now?\n")
                if not self.compute_if_first_sentences_has_higher_cosine_similarity(_in, random_fact, question):
                    print("Ok we'll move onto questions now!")
                    break
                else:
                    print("I'm glad you like my facts!")
        while True:
            question = input(
                "\nDo you have any questions? Feel free to ask me things like 'How can I get a license?', 'What was the first motorcycle?',  'Tell me about licenses', etc. I'll do my best to answer it!\nIf you don't have any questions say I have no questions!\n")
            done_with_questions = ["I have no questions", "I'm all done", "I don't have any"]

            # Might need to tweak the similarity score threshold later
            if self.compute_highest_cosine_similarity(done_with_questions, question) >= 0.5:
                return
            else:
                self.ask_question(question)

    def thank_user_for_their_time(self):
        print(
            f"\nIt was great getting to talk to you {self.name}, I had a lot fun! Hopefully you were able to learn more about motorcycles,"
            f"feel free to come back and talk to me, I get lonely!")
