import datetime
import json
import os
from typing import Dict, List

import elasticsearch
import psycopg2
import psycopg2.extras
import requests
from backoff_ import backoff
from config import Database, Genre, Movies, Person, logger, state_map
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from psycopg2 import sql
from state import JsonFileStorage, State

load_dotenv()


class ElasticsearchPreparation:
    def __init__(self):
        self.client = Elasticsearch(
            "http://{0}:{1}".format(os.environ.get('ES_HOST'), os.environ.get('ES_PORT')),
        )
        logger.info(self.client.ping())

    @backoff(logger)
    def create_index(self, index_name: str, settings: Dict) -> bool:
        """Создать индекс для Elasticsearch"""
        created = False
        try:
            if not self.client.indices.exists(index_name):
                logger.info("Creating index {0} with schema {1}".format(index_name, settings))
                self.client.indices.create(index=index_name, ignore=400, body=settings)
            created = True
        except elasticsearch.exceptions.ConnectionError as ex:

            logger.error(str(ex))
        finally:
            return created


@backoff(logger)
def postgres_connection(database):
    setting = {'dbname': database.psql_dbname,
               'user': database.psql_user,
               'password': database.psql_password,
               'host': database.psql_host,
               'port': int(database.psql_port)}
    return psycopg2.connect(**setting)


class PostgresExtractor:
    def __init__(self, query: str, batch_size: int, index_name: str):
        self.query = query
        self.index_name = index_name
        self.database = Database()
        self.batch_size = batch_size
        self.conn = postgres_connection(self.database)

    def get_state(self):
        storage = JsonFileStorage(state_map[self.index_name])
        state = State(storage)
        return {'state': state.get_state('modified')}

    def extract_data(self):
        """Генератор пачек данных"""
        conn = postgres_connection(self.database)
        with conn.cursor() as curs:
            curs.execute(sql.SQL(self.query), self.get_state())
            while rows := curs.fetchmany(self.batch_size):
                yield rows


class DataTransform:
    def __init__(self, index_name: str):
        self.index_name = index_name

    def get_movie(self, rows: List[tuple]) -> List[dict]:
        result = []
        for row in rows:
            movie_info = Movies(*row)
            director = [d['person_name'] for d in movie_info.persons if d['person_role'] == 'director']
            actors_names = [a['person_name'] for a in movie_info.persons if a['person_role'] == 'actor']
            writers_names = [w['person_name'] for w in movie_info.persons if w['person_role'] == 'writer']
            actors = [{"id": a['person_id'], "name": a['person_name']}
                      for a in movie_info.persons if a['person_role'] == 'actor']
            writers = [{"id": w['person_id'], "name": w['person_name']}
                       for w in movie_info.persons if w['person_role'] == 'writer']
            res = {
                'id': movie_info.id,
                'imdb_rating': movie_info.rating,
                'genre': movie_info.genres,
                'title': movie_info.title,
                'description': movie_info.description,
                'director': director,
                'actors_names': actors_names,
                'writers_names': writers_names,
                'actors': actors,
                'writers': writers}
            result.append(res)
        return result

    def get_person(self, rows: List[tuple]) -> List[dict]:
        """Метод для возврата типа подходящего для ElasticSearch"""
        result = []
        for row in rows:
            person_info = Person(*row)
            res = {
                'id': person_info.id,
                'full_name': person_info.full_name,
                'roles': person_info.role,
                'film_ids': person_info.film_ids
            }
            result.append(res)
        return result

    def get_genre(self, rows: List[tuple]) -> List[dict]:
        result = []
        for row in rows:
            genre_info = Genre(*row)
            res = {
                'id': genre_info.id,
                'name': genre_info.name
            }
            result.append(res)
        return result

    def get_elasticsearch_type(self, rows: List[tuple]) -> List[dict]:
        """Метод для возврата типа подходящего для ElasticSearch"""
        if self.index_name == 'movies':
            return self.get_movie(rows)
        if self.index_name == 'person':
            return self.get_person(rows)
        if self.index_name == 'genre':
            return self.get_genre(rows)


def bulk(rows: List[dict], index_name: str) -> List[str]:
    """Создание запроса для закачивания данных в ElasticSearch"""
    query = []
    for row in rows:
        query.extend([json.dumps({'index': {'_index': index_name, '_id': row['id']}}), json.dumps(row)])
    return query


class ElasticsearchLoader:
    def __init__(self, url: str, index_name: str):
        self.url = url
        self.index_name = index_name

    def set_state(self):
        storage = JsonFileStorage(state_map[self.index_name])
        state = State(storage)
        state.set_state("modified", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @backoff(logger)
    def upload_to_elasticsearch(self, rows: list) -> None:
        """Закачивание данных в ElasticSearch через посыл запроса"""
        query = bulk(rows, self.index_name)

        response = requests.post(
            self.url + '_bulk',
            data='\n'.join(query) + '\n',
            headers={'Content-Type': 'application/x-ndjson'}
        )
        logger.info(response.text)
        if response.status_code == 200:
            self.set_state()






