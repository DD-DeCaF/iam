FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

# postgresql-dev is required for psycopg2
# openssh is required to generate rsa keys
RUN apk --no-cache add postgresql-dev openssh

RUN mkdir /app
WORKDIR /app

COPY Pipfile Pipfile.lock /app/
# g++ is required to build python gevent dependency
# git is required for github references in Pipenv (hopefully temporary)
RUN apk add --no-cache --virtual .build-deps g++ git \
    && pip install pipenv \
    && pipenv install --dev --system --deploy \
    && apk del .build-deps

COPY . /app

CMD ["gunicorn", "-c", "gunicorn.py", "iam.main:app"]
