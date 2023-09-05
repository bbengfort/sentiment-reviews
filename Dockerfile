FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update --yes
RUN apt-get install --yes postgresql-client
RUN apt-get install --yes gcc libc-dev build-essential libpq-dev python3-dev

RUN groupadd -r django && useradd -m -r -g django django
USER django

RUN mkdir /home/django/app
WORKDIR /home/django/app

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

USER root
RUN apt-get clean autoclean
RUN apt-get autoremove --yes
USER django

COPY ./ ./