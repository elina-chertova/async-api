import pytest

import testdata.index_map as index_map
import utils.helper as util


@pytest.fixture(scope='session', autouse=True)
async def load_data(es_client):
    indexes = index_map.ind_data
    for i in indexes.keys():
        bulk_query = await util.get_es_bulk_query(indexes[i], i)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
