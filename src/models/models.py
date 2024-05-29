import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Genre(Base):
    id: str
    name: str


class RelatedPersonMovie(Base):
    id: str
    roles: str


class Person(Base):
    """Model to represent Person objects."""
    id: str
    full_name: str
    roles: list[str]
    film_ids: list[str]

    class Config:
        orm_mode = True


class PersonInFilm(BaseModel):
    id: str
    name: str


class FilmById(Base):
    id: str
    title: str
    imdb_rating: float
    description: str
    genre: list[str]
    director: list[str]
    actors: list[PersonInFilm]
    writers: list[PersonInFilm]


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float


class GenreInFilm(BaseModel):
    id: str
    name: str