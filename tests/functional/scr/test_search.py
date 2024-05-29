from http import HTTPStatus

import pytest

import testdata.film_data as film
import testdata.genre_data as genre
import testdata.person_data as person


@pytest.mark.parametrize(
    'main_status, text, expected_answer',
    [
        (
            HTTPStatus.OK,
            film.search_film_text,
            film.search_film_text_res
        ),
        (
            HTTPStatus.NOT_FOUND,
            film.search_film_no_text,
            film.search_film_no_text_res
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_text_film(make_get_request, main_status, text, expected_answer):
    body, status = await make_get_request('films/search/?title={}&page[size]=50&page[number]=1'.format(text))
    assert status == main_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'main_status, text, expected_answer',
    [
        (
            HTTPStatus.OK,
            genre.search_genre_text,
            genre.search_genre_text_res
        ),
        (
            HTTPStatus.NOT_FOUND,
            genre.search_genre_no_text,
            genre.search_genre_no_text_res
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_text_genre(make_get_request, main_status, text, expected_answer):
    body, status = await make_get_request('genres/search/?name={}&page[size]=50&page[number]=1'.format(text))
    assert status == main_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'main_status, text, expected_answer',
    [
        (
            HTTPStatus.OK,
            person.search_person_textname,
            person.search_person_textname_res
        ),
        (
            HTTPStatus.NOT_FOUND,
            person.search_person_no_textname,
            person.search_person_no_textname_res
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_person_textname(make_get_request, main_status, text, expected_answer):
    body, status = await make_get_request('people/search/?name={}&page[size]=50&page[number]=1'.format(text))
    assert status == main_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'main_status, text, expected_answer',
    [
        (
            HTTPStatus.OK,
            person.search_person_textrole,
            person.search_person_textrole_res
        ),
        (
            HTTPStatus.NOT_FOUND,
            person.search_person_no_textrole,
            person.search_person_no_textrole_res
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_person_textrole(make_get_request, main_status, text, expected_answer):
    body, status = await make_get_request('people/search/?role={}&page[size]=4&page[number]=1'.format(text))

    assert status == main_status

    if status != HTTPStatus.NOT_FOUND:
        assert len(body) == len(expected_answer)

        for i in body:
            assert i in expected_answer


@pytest.mark.parametrize(
    'main_status, text_name, text_role, expected_answer',
    [
        (
            HTTPStatus.OK,
            person.search_person_double_textname,
            person.search_person_double_textrole,
            person.search_person_textnamerole_res
        ),
        (
            HTTPStatus.NOT_FOUND,
            person.search_person_no_double_textname,
            person.search_person_no_double_textrole,
            person.search_person_no_textnamerole_res
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_person_textnamerole(make_get_request, main_status, text_name, text_role, expected_answer):
    body, status = await make_get_request('people/search/?name={}&role={}&page[size]=50&page[number]=1'.format(text_name, text_role))
    assert status == main_status
    assert body == expected_answer
