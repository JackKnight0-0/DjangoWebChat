FROM python:3.11.7-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_DISABLE_PIP_VESRION_CHECK 1
ENV PYTHONUNBUFFERED 1

WORKDIR DjangoChat

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .