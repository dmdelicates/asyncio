from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Character(Base):

    __tablename__ = 'characterd'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    birth_year = Column(String(10))
    gender = Column(String(15))
    height = Column(String(10))
    mass = Column(String(10))
    eye_color = Column(String(32))
    hair_color = Column(String(32))
    skin_color = Column(String(32))
    films = Column(String)
    homeworld = Column(String)
    species = Column(String)
    starships = Column(String)
    vehicles = Column(String)
