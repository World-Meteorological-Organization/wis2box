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

FROM eclipse-mosquitto:2.1.2-alpine

RUN apk update && \
    apk upgrade --no-cache && \
    mkdir -p /data/wis2box/mosquitto/config && \
    mkdir -p /data/wis2box/mosquitto/log && \
    mkdir -p /data/wis2box/mosquitto/data && \
    ln -s /mosquitto /data/wis2box/mosquitto

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

# ensure permissions set for mosquitto
RUN chown -R mosquitto:mosquitto /mosquitto

USER mosquitto
