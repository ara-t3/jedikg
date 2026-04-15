FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y unzip

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY reasoners/*.zip /tmp/zips/

RUN unzip /tmp/zips/konclude.zip -d /app/konclude

RUN mkdir kg-saf

RUN mkdir -p kg-saf/jdex

COPY ./jdex ./kg-saf/jdex
