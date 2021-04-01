import re

from botapi.Motorcycle import get_motorcycles


class MotorcycleFinder:
    def __init__(self, ner):
        self.categories = []
        self.budget = None
        self.seat_height = None
        self.year_start = 1800
        self.year_end = 1800
        self.engine_types = []
        self.order_by = []
        self.ner = ner
        self.review_categories = ["ride_quality", "engine", "reliability", "value", "equipment"]

    def begin_questions(self):
        print(
            "If the question isn't important for you please type in N/A and it won't be used when finding your perfect bike\n")
        self.get_category()
        self.get_budget()
        self.get_seat_height()
        self.get_year_range()
        self.get_engine_type()
        self.get_ranking_preference()
        return self.get_top_3_motorcycles()

    def get_category(self):
        category = input(
            "What category of motorcycle are you looking for? Supported Inputs (feel free to enter multiple):\n"
            "Standard, Dual sport, Naked, Sport bike, Supermoto, Enduro, Cruiser, Sport touring, Adventure, Electric\n")
        categories = self.parse_category_input(category)
        if categories is not None:
            while not categories:
                category = input("Couldn't detect a valid category, please try again. Valid categories:\n"
                                 "Standard, Dual sport, Naked, Sport bike, Supermoto, Enduro, Cruiser, Sport touring, Adventure, Electric\n")
                categories = self.parse_category_input(category)
            self.categories = categories

    def parse_category_input(self, _in):
        category_list = []
        if str.lower(_in) != 'n/a':
            if re.search(r"(standard)", _in, re.IGNORECASE):
                category_list.append("Standard")
            if re.search(r"(dual)", _in, re.IGNORECASE):
                category_list.append("Dual sport")
            if re.search(r"(naked)", _in, re.IGNORECASE):
                category_list.append("Naked")
            if re.search(r"(sport[- ]?bike)|(sport(?!.*touring){0})", _in, re.IGNORECASE):
                category_list.append("Sport bike")
            if re.search(r"(supermoto)|(sumo)", _in, re.IGNORECASE):
                category_list.append("Supermoto")
            if re.search(r"(enduro)", _in, re.IGNORECASE):
                category_list.append("Enduro")
            if re.search(r"(cruiser)|(crusier)", _in, re.IGNORECASE):
                category_list.append("Cruiser")
            if re.search(r"(sport[- ?]touring)", _in, re.IGNORECASE):
                category_list.append("Sport touring")
            if re.search(r"(naked)", _in, re.IGNORECASE):
                category_list.append("Naked")
            if re.search(r"(adventure)", _in, re.IGNORECASE):
                category_list.append("Adventure")
            if re.search(r"(electric)", _in, re.IGNORECASE):
                category_list.append("Electric")
        else:
            category_list = None
        return category_list

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

    # TODO: The NER is a little finicky - 2000 to 2009 doesn't get detected as a date but 2000 to 2010 does (maybe try the medium dataset for this to see if it works better?)
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
                    try:
                        index = ranking_preference.index("ride quality")
                        if index:
                            ranking_preference[index] = "ride_quality"
                    except ValueError:
                        pass
                    if len(ranking_preference) < 5:
                        for ranking in self.review_categories:
                            if ranking not in ranking_preference:
                                ranking_preference.append(ranking)
                    self.order_by = ranking_preference
                    return
                ranking_preference = input(
                    "Couldn't detect a valid ranking. Please input any combination of the following in order of most important to least:\n"
                    "ride quality, engine, reliability, value, and equipment\n")

    def get_top_3_motorcycles(self):
        response = get_motorcycles(3, categories=self.categories, budget=self.budget, seat_height=self.seat_height,
                                   year_start=self.year_start, year_end=self.year_end, engine_types=self.engine_types,
                                   order_by=self.order_by)

        num2word = {2: 'two', 3: 'three'}
        if response:
            print(
                f"\nThe top {f'{num2word[len(response)]} motorcycles' if len(response) > 1 else 'motorcycle'} for you {'are' if len(response) > 1 else 'is'}:")
            for index, moto in enumerate(response, start=1):
                print(
                    f"{index}. {moto['year_start']}-{'current' if int(moto['year_end']) == 0 else moto['year_end']} {moto['make']} {moto['model']}\n"
                    f"\tPrice(estimate): {moto['price']}\tCategory: {moto['category']}\tEngine Type: {moto['engine_type']}\tEngine Size: {moto['engine_size']}\tTank Range: {moto['tank_range']}\n"
                    f"\tHorsepower: {moto['power']}\tSeat Height: {moto['seat_height']}\tWeight: {moto['weight']}\n")
                review = moto['review']
                print(f"\tReview Info (out of 5):")
                print(f"\t\tOverall Rating: {review['overall_rating']}")

                order_by = [" ".join(order.split("_")) for order in self.order_by]
                for indx, order in enumerate(order_by):
                    print(f"\t\t{order}: {review[self.order_by[indx]]}")
                print()
                return response
                # TODO: ASK IF THEY WANT TO SEARCH AGAIN
        else:  # TODO: IMPLEMENT THIS
            input("Could not find any motorcycles matching your criteria. Let's try again!")
