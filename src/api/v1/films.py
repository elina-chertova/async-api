from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from api.v1.error import FILM_NOT_FOUND, PAGE_NOT_FOUND
from api.v1.paginator import Paginator
from services.film import FilmService, get_film_service

router = APIRouter()


class GenreInFilm(BaseModel):
    id: str
    name: str


class PersonInFilm(BaseModel):
    id: str
    name: str


class FilmById(BaseModel):
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


@router.get('/',
            summary="All movies",
            response_description="Movies' title and rating",
            description="Information about all movies in the service")
async def all_films(request: Request,
                    person_service: FilmService = Depends(get_film_service),
                    paginator: Paginator = Depends(),
                    sort: str = Query('imdb_rating:desc', description='Sorted fields in the format field:asc/desc'),
                    genre: str = Query('', description='Filter by genre')) -> list[Film]:
    """
    Returns the list of people participating in any movies.

    """
    films = await person_service.get_all_films(page=paginator.page_number, sort=sort, genre=genre,
                                               page_size=paginator.page_size, request=request)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return films


@router.get('/search/',
            summary="Film search",
            response_description="Movies' title and rating",
            description="Full text search for movies",
            tags=['Full text search'])
async def all_films(request: Request,
                    person_service: FilmService = Depends(get_film_service),
                    title: str = Query(None, description="Enter film's title or its part"),
                    paginator: Paginator = Depends()) -> list[Film]:
    """
    Returns the list of people participating in any movies.

    """
    films = await person_service.get_all_films(title=title, page=paginator.page_number,
                                               page_size=paginator.page_size, request=request)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return films


@router.get('/{film_id}', response_model=FilmById,
            summary="Film search by id",
            response_description="Movies' title, rating, description, genre, director, actors and writers",
            description="Information about film by its id",
            tags=['ID search'])
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmById:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return FilmById(id=film.id, title=film.title, imdb_rating=film.imdb_rating,
                    description=film.description, genre=film.genre, director=film.director,
                    actors=film.actors, writers=film.writers)
