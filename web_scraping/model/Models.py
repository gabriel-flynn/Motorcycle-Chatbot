import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Motorcycle(Base):
    __tablename__ = 'motorcycles'

    id = Column(Integer, primary_key=True)
    make = Column(String(40))
    model = Column(String(40))
    year_start = Column(Integer)
    year_end = Column(Integer)
    price = Column(Integer)
    category = Column(String(40))
    engine_size = Column(String(40))
    engine_type = Column(String(40))
    insurance_group = Column(Integer)
    mpg = Column(Integer)
    tank_range = Column(Integer)
    power = Column(Integer)
    seat_height = Column(Integer)
    weight = Column(Integer)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    review = relationship("Review", backref="reviews")


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    overall_rating = Column(Integer)
    overall_rating_review_text = Column(Text)
    ride_quality = Column(Integer)
    ride_quality_review_text = Column(Text)
    engine = Column(Integer)
    engine_review_text = Column(Text)
    reliability = Column(Integer)
    reliability_review_text = Column(Text)
    value = Column(Integer)
    value_review_text = Column(Text)
    equipment = Column(Integer)
    equipment_review_text = Column(Text)


load_dotenv()
db_user = os.getenv('db_user')
db_pass = os.getenv('db_pass')
db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')
engine = create_engine(f"mysql://{db_user}:{db_pass}@{db_host}/{db_name}", echo=True)

Base.metadata.create_all(engine)
