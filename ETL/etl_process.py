import os
import time

from dotenv import load_dotenv
from es_indexes import settings_film, settings_genre, settings_person
from etl_classes import (DataTransform, ElasticsearchLoader,
                         ElasticsearchPreparation, PostgresExtractor)
from sql_query import film_query, genre_query, person_query

load_dotenv()

BATCH_SIZE = 25
INDEX_MOVIE_NAME = 'movies'
INDEX_PERSON_NAME = 'person'
INDEX_GENRE_NAME = 'genre'


def etl(query: str, index_name: str, settings: dict) -> None:
    cl = ElasticsearchPreparation()
    postgr = PostgresExtractor(query, BATCH_SIZE, index_name)

    el = ElasticsearchLoader(os.environ.get('ES_URL'), index_name)
    cl.create_index(index_name=index_name, settings=settings)
    transf = DataTransform(index_name)
    with postgr.conn as pc:
        rows = postgr.extract_data()
        for row in rows:
            res = transf.get_elasticsearch_type(row)
            el.upload_to_elasticsearch(res)
    pc.close()


if __name__ == '__main__':
    while True:
        etl(film_query, INDEX_MOVIE_NAME, settings_film)
        etl(person_query, INDEX_PERSON_NAME, settings_person)
        etl(genre_query, INDEX_GENRE_NAME, settings_genre)
        time.sleep(10)

