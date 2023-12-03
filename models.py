from sqlalchemy import Column, DateTime, Integer, String

from app import db


class Temperature(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    time = Column(String(50))
    temperature = Column(String(6))

    def __str__(self):
        return self.name

class Log(db.Model):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    time = Column(String(50))
    content = Column(String(250))

    def __str__(self):
        return self.content
