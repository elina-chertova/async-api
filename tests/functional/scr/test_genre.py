import json
from http import HTTPStatus

import pytest

import testdata.genre_data as genre


@pytest.mark.parametrize(
    'genre_id, expected_answer',
    [
        (
                genre.genre_id,
                {'status': HTTPStatus.OK, 'body': genre.genre_id_res}
        ),
        (
                genre.genre_id_not_ex,
                {'status': HTTPStatus.NOT_FOUND, 'body': genre.genre_id_not_ex_res}
        )
    ]
)
@pytest.mark.asyncio
async def test_genre(make_get_request, genre_id, expected_answer):
    body, status = await make_get_request('genres/' + str(genre_id))
    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.asyncio
async def test_all_genre(
        make_get_request,
        expected_answer=None
):
    if expected_answer is None:
        expected_answer = [
            {
                "id": i["id"],
                "name": i["name"]
            } for i in genre.genre_data
        ]
    body, status = await make_get_request('genres/?page[size]=50&page[number]=1')

    assert status == HTTPStatus.OK
    assert len(body) == len(expected_answer)

    for elem in body:
        assert elem in expected_answer


@pytest.mark.asyncio
async def test_film_page_wrong(make_get_request):
    body, status = await make_get_request('genres/?page[size]=50&page[number]=0')
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_genre_cache(make_get_request, redis_client):
    _, _ = await make_get_request('genres/' + str(genre.genre_id))
    redis_key = "genre::guid::{id_}".format(id_=genre.genre_id)

    res = await redis_client.get(redis_key)
    res = json.loads(res.decode('utf8'))

    assert res['id'] == genre.genre_id
