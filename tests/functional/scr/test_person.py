import json
from http import HTTPStatus

import orjson
import pytest

import testdata.person_data as person


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                person.person_id,
                {'status': HTTPStatus.OK, 'body': person.person_id_res}
        ),
        (
                person.person_not_ex,
                {'status': HTTPStatus.NOT_FOUND, 'body': person.person_not_ex_res}
        )
    ]
)
@pytest.mark.asyncio
async def test_person(make_get_request, person_id, expected_answer):
    body, status = await make_get_request('people/' + str(person_id))
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                person.person_film_id,
                {'status': HTTPStatus.OK, 'body': person.person_film_id_res}
        ),
        (
                person.per_film_not_ex,
                {'status': HTTPStatus.NOT_FOUND, 'body': person.per_film_not_ex_res}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_film(make_get_request, person_id, expected_answer):
    body, status = await make_get_request('people/' + str(person_id) + '/films')
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                person.person_id,
                {'status': HTTPStatus.OK, 'body': person.person_id_res}
        ),
        (
                person.person_not_ex,
                {'status': HTTPStatus.NOT_FOUND, 'body': person.person_not_ex_res}
        )
    ]
)
@pytest.mark.asyncio
async def test_person(make_get_request, person_id, expected_answer):
    body, status = await make_get_request('people/' + str(person_id))
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.asyncio
async def test_all_people(make_get_request, expected_answer=person.people_data):
    body, status = await make_get_request('people/?page[size]=60&page[number]=1')
    assert status == HTTPStatus.OK
    assert body == expected_answer


@pytest.mark.asyncio
async def test_person_page(make_get_request):
    _, status = await make_get_request('people/?page[size]=50&page[number]=1')
    assert status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_person_page_num_l_wrong(make_get_request):
    _, status = await make_get_request('people/?page[size]=50p&page[number]=0')
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_person_page_num_g_wrong(make_get_request):
    _, status = await make_get_request('people/?page[size]=1&page[number]=61')
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_person_page_size_zero_wrong(make_get_request):
    _, status = await make_get_request('people/?page[size]=0&page[number]=1')
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_person_page_size_too_wrong(make_get_request):
    _, status = await make_get_request('people/?page[size]=101&page[number]=1')
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_person_cache(make_get_request, redis_client):
    _, _ = await make_get_request('people/' + str(person.person_id))
    redis_key = "person::guid::{id_}".format(id_=person.person_id)
    res = await redis_client.get(redis_key)
    res = json.loads(res.decode('utf8'))
    assert res['id'] == person.person_id


@pytest.mark.asyncio
async def test_people_cache(make_get_request, redis_client):
    _, _ = await make_get_request('people/?page[size]=60&page[number]=1')
    redis_key = "person::page_size::60::page_number::1::role::None::name::None"

    res = await redis_client.get(redis_key)
    res = orjson.loads(res.decode('utf8'))

    assert res == person.people_data


@pytest.mark.asyncio
async def test_person_film_cache(make_get_request, redis_client):
    body, _ = await make_get_request('people/' + str(person.person_film_id) + '/films')
    redis_key = "person::films::guid::{id_}".format(id_=person.person_film_id)

    res = await redis_client.get(redis_key)
    res = json.loads(res.decode('utf8'))

    assert res == person.person_film_id_res
