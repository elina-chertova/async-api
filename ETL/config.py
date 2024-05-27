import datetime
import logging
import uuid
from dataclasses import dataclass

from pydantic import BaseSettings

logging.basicConfig(filename="elastic.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger('log')


class Database(BaseSettings):
    psql_dbname: str = "movies_db"
    psql_user: str = "app"
    psql_password: str = "123qwe"
    psql_host: str = "127.0.0.1"
    psql_port: str = "5432"


state_map = {
  'movies': 'state_film.json',
  'person': 'state_person.json',
  'genre': 'state_genre.json'
}


@dataclass
class Movies:
    id: uuid.UUID
    title: str
    description: str
    rating: int
    type: str
    created: datetime.datetime
    modified: datetime.datetime
    persons: list
    genres: list


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    role: list
    film_ids: list
    modified: datetime.datetime


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    modified: datetime.datetime
