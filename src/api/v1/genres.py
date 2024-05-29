from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.v1.error import GENRE_NOT_FOUND, PAGE_NOT_FOUND
from api.v1.paginator import Paginator
from models.models import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/',
            summary="All genres",
            response_description="Genres' name",
            description="Information about all genres in the service")
async def all_genres(request: Request,
                     genre_service: GenreService = Depends(get_genre_service),
                     paginator: Paginator = Depends()):
    """
    Returns the list of genres from all movies.

    """
    genre = await genre_service.get_all_objects(page=paginator.page_number,
                                                page_size=paginator.page_size, request=request)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return genre


@router.get('/search/',
            summary="Genre search",
            response_description="Genres' name",
            description="Full text search for genres",
            tags=['Full text search'])
async def all_genres(request: Request,
                     genre_service: GenreService = Depends(get_genre_service),
                     name: str = Query(None, description="Enter the name/part of name's genre"),
                     paginator: Paginator = Depends()):
    """
    Returns the list of genres from all movies.

    """
    genre = await genre_service.get_all_objects(name=name, page=paginator.page_number,
                                                page_size=paginator.page_size, request=request)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PAGE_NOT_FOUND)

    return genre


@router.get('/{genre_id}', response_model=Genre,
            summary="Genre search by id",
            response_description="Genres' name",
            description="Information about genre by its id",
            tags=['ID search'])
async def genre_details(genre_id: str,
                        genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Returns the info about genre from its id.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return Genre(id=genre.id, name=genre.name)
