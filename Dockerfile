FROM python:3.9

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /usr/src/app

RUN pip install --upgrade pip
COPY /src/requirements.txt .
RUN pip install -r requirements.txt

COPY ./src .

COPY ./tests tests
