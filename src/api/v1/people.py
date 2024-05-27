from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from api.v1.error import FILM_NOT_FOUND, PAGE_NOT_FOUND, PERSON_NOT_FOUND
from api.v1.paginator import Paginator
from services.person import PersonService, get_person_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float


class Person(BaseModel):
    id: str
    full_name: str
    role: list[str]
    film_ids: list[str]

    class Config:
        orm_mode = True


@router.get('/',
            summary="All people",
            response_description="Person' full name, them roles and movies' links",
            description="All people from any movies")
async def all_people(request: Request,
                     person_service: PersonService = Depends(get_person_service),
                     paginator: Paginator = Depends()):
    """
    Returns the list of people participating in any movies.
    """
    person = await person_service.get_all_people(request=request, page_size=paginator.page_size,
                                                 page=paginator.page_number)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return person


@router.get('/search/',
            summary="Person search",
            response_description="Person' full name, them roles and movies' links",
            description="Full text search for people",
            tags=['Full text search'])
async def all_people(request: Request,
                     person_service: PersonService = Depends(get_person_service),
                     name: str = Query(None, description='Enter the name/part of name'),
                     role: str = Query(None, description="Enter person's role (director/writer/actor)"),
                     paginator: Paginator = Depends()):
    """
    Returns the list of people participating in any movies.
    """
    person = await person_service.get_all_people(name=name, role=role,
                                                 request=request, page_size=paginator.page_size,
                                                 page=paginator.page_number)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return person


@router.get('/{person_id}', response_model=Person,
            summary="Person search by id",
            response_description="Person' full name, them roles and movies' links",
            description="Information about person by its id",
            tags=['ID search'])
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)) -> Person:
    """
    Returns the info about person from them ids.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    return Person(id=person.id, full_name=person.full_name, role=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/films/',
            summary="Movie search from person id",
            response_description="Movies' title and rating",
            description="Information about movies in which a person participated",
            tags=['ID search'])
async def film_details(request: Request,
                       person_id: str,
                       person_service: PersonService = Depends(get_person_service)) -> Film:
    """
    Returns the info about person from them ids.
    """
    film = await person_service.get_film_by_person_id(person_id=person_id, request=request)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return film
