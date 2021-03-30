import re
from botapi.Motorcycle import get_motorcycles


class MotorcycleFinder:
    def __init__(self, ner):
        self.category = None
        self.budget = None
        self.seat_height = None
        self.year_start = 1800
        self.year_end = 1800
        self.engine_types = []
        self.order_by = []
        self.ner = ner

    def begin_questions(self):
        print(
            "If the question isn't important for you please type in N/A and it won't be used when finding your perfect bike")
        self.get_category()
        self.get_budget()
        self.get_seat_height()
        self.get_year_range()
        self.get_engine_type()
        self.get_ranking_preference()
        self.get_top_3_motorcycles()

    def get_category(self):
        category = input("What category of motorcycle are you looking for? Supported Inputs (feel free to enter multiple):\n"
                         "Standard, Dual sport, Supermotard, Sport bike, Cruiser, Scooter, Streetfighter, ")
        if str.lower(category) != 'n/a':
            self.category = category

    # TODO: $25000 doesn't seem to work
    def get_budget(self):
        budget = input("What is your budget in USD?\n")
        doc = self.ner(budget)

        if str.lower(budget) != 'n/a':
            found = False
            while not found:
                for ent in doc.ents:
                    if ent.label_ == 'MONEY' or ent.label_ == 'CARDINAL' or ent.label_ == 'DATE':
                        budget = re.sub(r'[$,]+', '', ent.text)
                        found = True
                        break
                if not found:
                    budget = input(
                        "Couldn't detect a valid budget input. Please input something like 'My budget is $5,000' or '5,000', etc.\n")
                    doc = self.ner(budget)
            self.budget = float(budget)

    def get_seat_height(self):
        seat_height = input(
            "What is the max seat height you're looking for? (in inches - 31 or less is considered a low seat height, less than 34 is considered medium and anything 34 and above is considered tall)\n")
        doc = self.ner(seat_height)
        if str.lower(seat_height) != 'n/a':
            found = False
            while not found:
                for ent in doc.ents:
                    if ent.label_ == 'CARDINAL':
                        seat_height = re.sub(r'[^0-9]+', '', ent.text)
                        found = True
                if not found:
                    seat_height = input(
                        "Couldn't detect a valid seat height. Please input something like 30in, 30, etc.\n")
                    doc = self.ner(seat_height)
            self.seat_height = int(seat_height)

    # TODO: The NER is a little finicky - 2000 to 2009 doesn't get detected as a date but 2000 to 2009 does (maybe try the medium dataset for this to see if it works better?)
    def get_year_range(self):
        years = input(
            "What is the year range you're looking for? Ex. I'm looking for one between 2000-2009, 2000 to 2009, 2000 2009, etc.  \n"
            "If you only care about the start or end range then use 1800 as a placeholder value like so: 1800-2009, 2000-1800, 2000 to 1800, 2000 1800\n"
            "Again is this isn't important to you then just type N/A\n")
        doc = self.ner(years)

        if str.lower(years) != 'n/a':
            found = False
            while not found:
                for ent in doc.ents:
                    if ent.label_ == 'DATE':
                        years_list = re.findall(r'[0-9]+', ent.text)
                        year_start = years_list[0]
                        year_end = years_list[1]
                        found = True
                        break
                if not found:
                    years = input(
                        "Couldn't detect a valid year range. Please input something like 2000-2009 2000 to 2009, 2000 2009, etc.\n")
                    doc = self.ner(years)
            self.year_start = int(year_start)
            self.year_end = int(year_end)

    def get_engine_type(self):
        engine_types = str.lower(input("Is there a specific engine type you're looking for? If not say N/A\n"
                                       "Possible Options are: box2, electric, flat2, flat4, flat6, i1, i2, i3, i4, i6, LTwin, transverse4, v4 and vtwin\n"
                                       "If you'd like to specify multiple you can say I'm interested in the i4, v4 or you can say I'm interested in the i4 and v4, etc.\n"))

        if str.lower(engine_types) != 'n/a':
            while True:
                engine_types = re.findall(
                    r'(box2|electric|flat2|flat4|flat6|i1|i2|i3|i4|i6|LTwin|transverse4|v4|vtwin)', engine_types)
                if engine_types:
                    self.engine_types = engine_types
                    return
                engine_types = input(
                    "Couldn't detect a valid engine type. Please input any combination of the following:\n"
                    "box2, electric, flat2, flat4, flat6, i1, i2, i3, i4, i6, LTwin, transverse4, v4 and vtwin\n")

    def get_ranking_preference(self):
        ranking_preference = input("Please rank the following criteria from most important to least important to you:\n"
                                   "ride quality, engine, reliability, value, and equipment\n")

        if str.lower(ranking_preference) != 'n/a':
            while True:
                ranking_preference = re.findall(
                    r'(ride quality|engine|reliability|value|equipment)', ranking_preference)
                if ranking_preference:
                    index = ranking_preference.index("ride quality")
                    if index:
                        ranking_preference[index] = "ride_quality"
                    self.order_by = ranking_preference
                    return
                ranking_preference = input(
                    "Couldn't detect a valid ranking. Please input any combination of the following in order of most important to least:\n"
                    "ride quality, engine, reliability, value, and equipment\n")

    def get_top_3_motorcycles(self):
        get_motorcycles(3, category=self.category, budget=self.budget, seat_height=self.seat_height,
                        year_start=self.year_start, year_end=self.year_end, engine_types=self.engine_types,
                        order_by=self.order_by)
