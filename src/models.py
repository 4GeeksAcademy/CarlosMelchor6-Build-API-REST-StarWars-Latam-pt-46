from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
import datetime
from sqlalchemy import Text
from typing import List
from sqlalchemy import Table
from sqlalchemy import Column

db = SQLAlchemy()

# Tabla de asociación entre usuarios y planetas favoritos
user_planet_favorites = Table(
    "user_planet_favorites",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("planet_id", ForeignKey("planets.id"), primary_key=True)
)
# Tabla de asociación entre usuarios y personas favoritas
user_people_favorites = Table(
    "user_people_favorites",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("person_id", ForeignKey("people.id"), primary_key=True)
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    user_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(120),nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    subscription_date: Mapped[datetime.datetime] = mapped_column(DateTime)


    # Favorite Relationship
    favorite_planets: Mapped[List["Planets"]] = relationship(
        secondary=user_planet_favorites, backref="favorited_by_users"
    )

    favorite_people: Mapped[List["People"]] = relationship(
        secondary=user_people_favorites, backref="favorited_by_users"
    )

    def __init__(self,email, password, user_name, first_name, last_name):
        self.email = email
        self.password = password
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = True
        self.subscription_date = datetime.datetime.utcnow()

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_name": self.user_name,
            "is_active": self.is_active
        }

class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name_of_planets: Mapped[str] = mapped_column(String(120), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name_of_planets": self.name_of_planets
        }

class People(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name_of_people: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name_of_people": self.name_of_people
        }