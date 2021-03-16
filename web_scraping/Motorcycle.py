class Motorcycle:

    """
    :param make: manufacturer of the motorcycle
    :param model: model of the motorcycle
    :param year_start: start of this generation of motorcycle
    :param year_end: end of this generation of motorcycle
    :param price: price of this motorcycle if I were to go out and buy it today (based off kbb values)
    :param category: type of motorcycle (sport bike, adventure bike, naked bike, etc.)
    :param is_new: is a bike that is currently being produced/manufactured - might remove this later as this might complicate things a bit
    :param engine_size: size of the engine in cubic centimeters
    :param engine_type: engine type - might just keep this at v4, i4, i2, v-twin, etc. for now
    :param insurance_group: group from 1 to 17 (17 being the most expensive) the motorcycle is in
    :param mpg: mpg of the motorcycle
    :param tank_range: range the motorcycle can go on one tank
    :param power: bhp of the bike
    :param seat_height: seat height of the bike (in inches)
    :param weight: weight of the bike
    :param review: Review associated with the bike
    """
    def __init__(self, make, model, year_start, year_end, price, category, is_new, engine_size, engine_type, insurance_group, mpg, tank_range, power, seat_height, weight, review):
        self.review = review
        self.weight = weight
        self.seat_height = seat_height
        self.power = power
        self.range = tank_range
        self.mpg = mpg
        self.insurance_group = insurance_group
        self.engine_type = engine_type
        self.engine_size = engine_size
        self.make = make
        self.model = model
        self.year_start = year_start
        self.year_end = year_end
        self.price = price
        self.category = category
        self.is_new = is_new
