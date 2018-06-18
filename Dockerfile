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
RUN apk add --update --no-cache openssl ca-certificates postgresql-dev openssh

# Install build dependencies. This could be combined wih the build in a single
# build step to reduce layer size, but is kept here to increase chances of
# cache hit and decrease build time at the cost of image size.
# `g++` is required for building `gevent`
# git is required for:
#   - github references in Pipfile (hopefully temporary)
RUN apk add --no-cache g++ git

# Install python build tools
# Bugs related to pip and pipenv:
# - The symlink is a temporary workaround for a bug in pipenv.
#   Still present as of pipenv==11.9.0.
# - pipenv is pinned to 11.10.0 to avoid the following issue:
#   https://github.com/pypa/pipenv/issues/2078
# - pip is pinned to 9.0.3 to avoid issues with `pipenv check` using deprecated
#   pip APIs
RUN set -x \
    && ln -sf /usr/local/bin/python /bin/python \
    && pip install --upgrade pip==9.0.3 setuptools wheel pipenv==11.10.0 \
    && rm -rf /root/.cache/pip

# Install python dependencies
COPY Pipfile* "${CWD}/"
RUN set -x \
    && pipenv install --system --dev --deploy \
    && rm -rf /root/.cache/pip

# Install the codebase
COPY . "${CWD}/"
RUN chown -R "${APP_USER}:${APP_USER}" "${CWD}"
