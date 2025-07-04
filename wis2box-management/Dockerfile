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

FROM ubuntu:jammy

LABEL maintainer="tomkralidis@gmail.com; mlimper@wmo.int"

ARG WIS2BOX_PIP3_EXTRA_PACKAGES
ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="cron bash vim curl git libffi-dev python3-cryptography libssl-dev libudunits2-0 apache2-utils python3 python3-pip curl python3-paho-mqtt python3-dateparser python3-tz python3-setuptools unzip"

RUN if [ "$WIS2BOX_PIP3_EXTRA_PACKAGES" = "None" ]; \
    then export WIS2BOX_PIP3_EXTRA_PACKAGES=echo; \
    else export WIS2BOX_PIP3_EXTRA_PACKAGES=pip3 install ${WIS2BOX_PIP3_EXTRA_PACKAGES}; \
    fi

# install dependencies
RUN apt-get update -y && apt-get install -y ${DEBIAN_PACKAGES} \
    # install wis2box data pipeline dependencies
    && pip3 install --no-cache-dir \
    https://github.com/wmo-cop/pyoscar/archive/refs/tags/0.9.0.zip \
    https://github.com/geopython/pygeometa/archive/refs/tags/0.16.0.zip \
    https://github.com/World-Meteorological-Organization/pywis-topics/archive/refs/tags/0.3.5.zip \
    # install cap validator
    && pip3 install --no-cache-dir capvalidator>=0.1.0-dev4 \
    # install shapely
    && pip3 install --no-cache-dir cython pygeos==0.13 \
    && pip3 install shapely \
    # install boto3 and botocore
    && pip3 install --no-cache-dir botocore boto3 \
    # cleanup
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/* \
    # create directory for wmdr codelists
    && mkdir -p /home/wis2box/wmdr-codelists 

# copy wmdr codelists
COPY ./wmdr-codelists /home/wis2box/wmdr-codelists

# copy the app
COPY . /app
# install wis2box
RUN cd /app \
    # install wis2box as an editable package in /app/wis2box
    && pip3 install -e . \
    # install wis2box plugins, if defined
    && $PIP_PLUGIN_PACKAGES \
    # add wis2box user
    && useradd -ms /bin/bash wis2box

WORKDIR /home/wis2box

# add wis2box.cron to crontab
COPY ./docker/wis2box.cron /etc/cron.d/wis2box.cron

RUN chmod 0644 /etc/cron.d/wis2box.cron && crontab /etc/cron.d/wis2box.cron

COPY ./docker/entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
