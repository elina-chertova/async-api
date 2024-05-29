import pytest

from settings import TestSettings

settings = TestSettings()
pytest_plugins = ["fixtures.client", "fixtures.load_data"]


@pytest.fixture(scope='session')
def make_get_request(session):
    async def inner(path: str, params: dict = None):
        params = params or {}
        url = '{protocol}://{host}:{port}/api/v1/{path}'.format(
            protocol='http',
            host=settings.service_host,
            port=settings.service_port,
            path=path
        )
        async with session.get(url, params=params) as response:
            body = await response.json()
            status = response.status
            return body, status

    return inner
