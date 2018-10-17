FROM dddecaf/wsgi-base:master

ENV APP_USER=giraffe

ARG UID=1000
ARG GID=1000

ARG CWD=/app
ENV PYTHONPATH=${CWD}/src
WORKDIR "${CWD}"

RUN addgroup -g "${GID}" -S "${APP_USER}" && \
    adduser -u "${UID}" -G "${APP_USER}" -S "${APP_USER}"

# Install alpine package dependencies
# - openssh is required to generate rsa keys
# - postgresql-dev is required for psycopg2
# - gcc is required for psycopg2
# - python3-dev is required for psycopg2
# - musl-dev is required for psycopg2
# - g++ is required for firebase-admin
RUN apk add --update --no-cache openssh postgresql-dev gcc python3-dev \
     musl-dev g++

# Install python dependencies
# `wsgi-requirements.txt` comes from the parent image and needs to be part of
# the `pip-sync` command otherwise those dependencies are removed.
COPY requirements.in dev-requirements.in ./
RUN set -eux \
    && pip-compile --generate-hashes dev-requirements.in \
    && pip-compile --generate-hashes requirements.in \
    && pip-sync /opt/wsgi-requirements.txt dev-requirements.txt \
        requirements.txt \
    && rm -rf /root/.cache/pip

# Install the codebase
COPY . "${CWD}/"
RUN chown -R "${APP_USER}:${APP_USER}" "${CWD}"
