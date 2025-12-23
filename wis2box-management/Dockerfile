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
    DEBIAN_PACKAGES="cron bash vim curl git libffi-dev python3-cryptography libssl-dev libudunits2-0 apache2-utils python3 python3-pip python3-venv curl python3-paho-mqtt python3-dateparser python3-tz python3-setuptools unzip"

# Install dependencies
RUN apt-get update -y && apt-get install -y ${DEBIAN_PACKAGES} \
    # Cleanup
    && apt autoremove -y \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -ms /bin/bash wis2box

# Create and activate a virtual environment for Python dependencies
RUN python3 -m venv /home/wis2box/venv \
    && chown -R wis2box:wis2box /home/wis2box/venv

USER wis2box
ENV PATH="/home/wis2box/venv/bin:$PATH"

# Install Python dependencies in the virtual environment
RUN . /home/wis2box/venv/bin/activate \
    && pip install --no-cache-dir \
    https://github.com/wmo-cop/pyoscar/archive/refs/tags/0.9.0.zip \
    https://github.com/geopython/pygeometa/archive/refs/tags/0.16.0.zip \
    https://github.com/World-Meteorological-Organization/pywis-topics/archive/refs/tags/0.3.5.zip \
    capvalidator==0.1.0-dev4 \
    shapely botocore boto3 \
    && if [ "$WIS2BOX_PIP3_EXTRA_PACKAGES" != "None" ]; then pip install ${WIS2BOX_PIP3_EXTRA_PACKAGES}; fi

# Copy WMDR codelists
COPY --chown=wis2box:wis2box ./wmdr-codelists /home/wis2box/wmdr-codelists

# Copy the app
COPY --chown=wis2box:wis2box . /app

# Install wis2box and plugins
RUN cd /app \
    && pip install -e . \
    && if [ -n "$PIP_PLUGIN_PACKAGES" ]; then pip install $PIP_PLUGIN_PACKAGES; fi

# Sync pywcmp bundle
RUN pywcmp bundle sync

WORKDIR /home/wis2box

# Add wis2box.cron to crontab
COPY --chown=wis2box:wis2box ./docker/wis2box.cron /etc/cron.d/wis2box.cron

USER root
RUN chmod 0644 /etc/cron.d/wis2box.cron && crontab /etc/cron.d/wis2box.cron
USER wis2box

# Copy entrypoint script
COPY --chown=wis2box:wis2box ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
