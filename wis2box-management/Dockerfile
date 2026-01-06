###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

FROM ubuntu:noble

LABEL maintainer="tomkralidis@gmail.com; mlimper@wmo.int"

ARG WIS2BOX_PIP3_EXTRA_PACKAGES
ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="bash vim curl git libffi-dev python3-cryptography libssl-dev libudunits2-0 apache2-utils python3 python3-pip curl python3-paho-mqtt python3-dateparser python3-tz python3-setuptools unzip python3-venv"

# install dependencies
RUN apt-get update -y && apt-get install -y ${DEBIAN_PACKAGES} \
    # cleanup
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/* \
    # create directory for wmdr codelists
    && mkdir -p /home/wis2box/wmdr-codelists \
    # Install Supercronic for job management
    && curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v0.2.41/supercronic-linux-amd64" \
    && chmod +x supercronic-linux-amd64 \
    && mv supercronic-linux-amd64 /usr/local/bin/supercronic

# copy wmdr codelists
COPY ./wmdr-codelists /home/wis2box/wmdr-codelists

# copy the app
COPY . /app

WORKDIR /home/wis2box

# create wis2box user with userid 1001
RUN groupadd -g 1001 -r wis2box && useradd -u 1001 -r -g wis2box wis2box \
    && chown -R wis2box:wis2box /app \
    && chown -R wis2box:wis2box /home/wis2box \
    && mkdir -p /data/wis2box \
    && chown -R wis2box:wis2box /data/wis2box

USER wis2box

# install wis2box in a virtual environment
RUN cd /app \
    && python3 -m venv /app/venv --system-site-packages \
    && . /app/venv/bin/activate \
    # install wis2box as an editable package in /app/wis2box
    && pip3 install -e . \
    # install wis2box plugins, if defined
    && $PIP_PLUGIN_PACKAGES \
    && pip3 install --no-cache-dir \
    https://github.com/wmo-cop/pyoscar/archive/refs/tags/0.9.0.zip \
    https://github.com/geopython/pygeometa/archive/refs/tags/0.16.0.zip \
    https://github.com/World-Meteorological-Organization/pywis-topics/archive/refs/tags/0.3.5.zip \
    && pip3 install --no-cache-dir capvalidator==0.1.0-dev4 cython shapely botocore boto3

RUN if [ "$WIS2BOX_PIP3_EXTRA_PACKAGES" = "None" ]; \
    then export WIS2BOX_PIP3_EXTRA_PACKAGES=echo; \
    else export WIS2BOX_PIP3_EXTRA_PACKAGES=pip3 install ${WIS2BOX_PIP3_EXTRA_PACKAGES}; \
    fi

# set PATH to include the virtual environment
ENV PATH="/app/venv/bin:${PATH}"

RUN pywcmp bundle sync

COPY ./docker/entrypoint.sh /home/wis2box/entrypoint.sh

ENTRYPOINT [ "/home/wis2box/entrypoint.sh" ]