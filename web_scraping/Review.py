class Review:

    """
    :param overall_rating: overall review rating of the bike
    :param overall_rating_review_text: text listed under the overall rating review
    :param ride_quality: score of the ride quality and brakes
    :param ride_quality_review_text: text listed under the ride quality review
    :param engine: score of the engine category in the review
    :param engine_review_text: text listed under the engine review
    :param reliability: score of the reliability and build quality category in the review
    :param reliability_review_text: text listed under the reliability review
    :param value: score of the value vs rivals
    :param value_review_text: text listed under the value review
    :param equipment: score of the equipment category in the review
    :param equipment_review_text: text listed under the equipment review
    """
    def __init__(self, overall_rating, overall_rating_review_text, ride_quality, ride_quality_review_text, engine, engine_review_text, reliability, reliability_review_text, value, value_review_text, equipment, equipment_review_text):
        self.equipment_review_text = equipment_review_text
        self.equipment = equipment
        self.value_review_text = value_review_text
        self.value = value
        self.reliability_review_text = reliability_review_text
        self.reliability = reliability
        self.engine_review_text = engine_review_text
        self.engine = engine
        self.ride_quality_review_text = ride_quality_review_text
        self.ride_quality = ride_quality
        self.overall_rating_review_text = overall_rating_review_text
        self.overall_rating = overall_rating
