## Запуск процесса через докер
Предварительно необходимо создать файл .env в директории src.

Пример:

```shell
ELASTIC_PORT=xxxx
REDIS_PORT=xxxx
```


Второй .env нужно создать в папке ETL.

Пример:
```shell
DB_NAME=db_name
DB_USER=user_name
DB_PASSWORD=password
DB_HOST=host
DB_PORT=xxxx
ES_PORT=xxxx
ES_HOST=host
ES_URL=elasticsearch_url
```

Для запуска ETL с сохранением состояния процесса нужно добавить 3 файла:
1. state_film.json
2. state_genre.json
3. state_person.json
Пример содержания каждого из предыдущих файлов:
{"modified": "2022-10-09 18:31:23"}


### Далее из корня проекта запустить команду: 
docker-compose up -d


## Запуск тестирования через докер
1. Предварительно необходимо создать файл .env по аналогии с .env.example в директориях src и tests.

2. Для запуска тестирования необходимо запустить из папки tests/functional команду:

```docker-compose up -d```


## Документация API
http://localhost:8000/api/openapi


