FROM python:3.6-alpine

# g++ is required to build python gevent dependency
# postgresql-dev is required for psycopg2
RUN apk --update add g++ postgresql-dev && rm -rf /var/cache/apk/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN mkdir /app
WORKDIR /app
COPY . /app

CMD ["gunicorn", "-c", "gunicorn.py", "iam.main:app"]
