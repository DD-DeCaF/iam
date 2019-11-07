FROM dddecaf/postgres-base:master

ENV APP_USER=giraffe

ARG UID=1000
ARG GID=1000

ARG CWD=/app
ENV PYTHONPATH=${CWD}/src
WORKDIR "${CWD}"

RUN addgroup -g "${GID}" -S "${APP_USER}" && \
    adduser -u "${UID}" -G "${APP_USER}" -S "${APP_USER}"

# Install openssh to be able to generate rsa keys
RUN apk add --update --no-cache openssh

# Install python dependencies
COPY requirements ./requirements
RUN set -eux \
    # build-base is required to build grpcio->firebase-admin
    && apk add --no-cache --virtual .build-deps build-base \
    && pip-sync requirements/requirements.txt \
    # Remove build dependencies to reduce layer size.
    && apk del .build-deps

# Install the codebase
COPY . "${CWD}/"
RUN chown -R "${APP_USER}:${APP_USER}" "${CWD}"
