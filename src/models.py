import os
import sys
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from eralchemy2 import render_er
from datetime import datetime, timezone

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    favorite_planets = db.relationship('Planet_Favorite', backref="user", lazy=True)
    favorite_people = db.relationship('People_Favorite', backref="user", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorite_planets": [fav.serialize() for fav in self.favorite_planets]
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    diameter = db.Column(db.String(50), nullable=False)
    rotation_period = db.Column(db.String(50), nullable=False)
    orbital_period = db.Column(db.String(50), nullable=False)
    gravity = db.Column(db.String(50), nullable=False)
    population = db.Column(db.String(50), nullable=False)
    climate = db.Column(db.String(100), nullable=False)
    terrain = db.Column(db.String(100), nullable=False)
    surface_water = db.Column(String(50), nullable=False)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    edited = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    favorites = relationship('Planet_Favorite', back_populates='planet')

class Planet_Favorite(db.Model):
    __tablename__ = 'planet_favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet = db.relationship("Planet", backref="planet_favorite", lazy=True)

    def __repr__(self):
        return '<Planet_Favorite %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "planet": self.planet.serialize() if self.planet else None,
        }

class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.String(50), nullable=False)
    eye_color = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    hair_color = db.Column(db.String(50), nullable=False)
    height = db.Column(db.String(20), nullable=False)
    mass = db.Column(db.String(40), nullable=False)
    skin_color = db.Column(db.String(50), nullable=False)
    homeworld = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    edited = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    favorites = relationship('People_Favorite', back_populates='people')

class People_Favorite(db.Model):
    __tablename__ = 'people_favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    people = db.relationship("People", backref="people_favorite", lazy=True)

    def __repr__(self):
        return '<People_Favorite %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people_id": self.people_id,
            "people": self.people.serialize() if self.people else None,
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
