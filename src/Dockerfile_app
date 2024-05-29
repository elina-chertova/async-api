FROM python:3.9

RUN mkdir -p /opt/app
ADD requirements.txt /opt/app

WORKDIR /opt/app

RUN pip install -r requirements.txt
ADD . /opt/app

#RUN #useradd -ms /bin/bash web && chown -R web /var/log && chown -R web /var/tmp && chown -R web /opt/app
COPY .. .
#USER web
