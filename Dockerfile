FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED=1

ENV APP_USER=giraffe

ARG UID=1000
ARG GID=1000

ARG CWD=/app
ENV PYTHONPATH=${CWD}/src
WORKDIR "${CWD}"

RUN addgroup -g "${GID}" -S "${APP_USER}" && \
    adduser -u "${UID}" -G "${APP_USER}" -S "${APP_USER}"

# Install alpine package dependencies
# postgresql-dev is required for psycopg2
# openssh is required to generate rsa keys
# g++ is required for building gevent
RUN apk add --update --no-cache openssl ca-certificates postgresql-dev openssh \
    g++

# Install python build tools
RUN pip install --upgrade pip setuptools wheel pip-tools

# Install python dependencies
# `wsgi-requirements.txt` comes from the parent image and needs to be part of
# the `pip-sync` command otherwise those dependencies are removed.
COPY requirements.in dev-requirements.in ./
RUN set -eux \
    && pip-compile --generate-hashes \
        --output-file dev-requirements.txt dev-requirements.in \
    && pip-compile --generate-hashes \
        --output-file requirements.txt requirements.in \
    && pip-sync dev-requirements.txt requirements.txt \
    && rm -rf /root/.cache/pip

# Install the codebase
COPY . "${CWD}/"
RUN chown -R "${APP_USER}:${APP_USER}" "${CWD}"
