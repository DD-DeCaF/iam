FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

# g++ is required to build python gevent dependency
# postgresql-dev is required for psycopg2
# openssh is required to generate rsa keys
# git is required for github references in requirements.txt (hopefully temporary)
RUN apk --update add g++ postgresql-dev openssh git && rm -rf /var/cache/apk/*

RUN mkdir /app
WORKDIR /app

RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --dev --system --deploy

COPY . /app

CMD ["gunicorn", "-c", "gunicorn.py", "iam.main:app"]
