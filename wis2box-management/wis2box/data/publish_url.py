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

import base64
from datetime import timezone
import hashlib
import ipaddress
import json
import logging
from pathlib import Path, PurePosixPath
import socket
from urllib.parse import unquote, urlsplit

import click
from dateutil.parser import isoparse
from shapely.geometry import shape
import requests

from wis2box import cli_helpers
from wis2box.data.base import BaseAbstractData
from wis2box.data_mappings import get_data_mappings

LOGGER = logging.getLogger(__name__)


def _validate_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise click.ClickException('URL must be an absolute HTTP or HTTPS URL')
    if parsed.username or parsed.password:
        raise click.ClickException('URL must not contain embedded credentials')
    try:
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        addresses = {
            ipaddress.ip_address(result[4][0])
            for result in socket.getaddrinfo(
                parsed.hostname, port, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as err:
        raise click.ClickException(f'Unable to resolve URL host: {err}') from err
    if not addresses or any(not address.is_global for address in addresses):
        raise click.ClickException('URL host must resolve only to public IP addresses')
    return url


def _read_integrity(url: str) -> tuple[int, str]:
    digest = hashlib.sha512()
    length = 0
    try:
        with requests.get(url, stream=True, timeout=(10, 60),
                          headers={'Accept-Encoding': 'identity'},
                          allow_redirects=False) as response:
            if 300 <= response.status_code < 400:
                raise click.ClickException(
                    'URL redirects are not supported; provide the final URL')
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    digest.update(chunk)
                    length += len(chunk)
    except requests.RequestException as err:
        raise click.ClickException(f'Unable to read URL: {err}') from err

    if length == 0:
        raise click.ClickException('The URL returned an empty resource')

    return length, base64.b64encode(digest.digest()).decode('ascii')


def _read_geometry(filepath: Path) -> dict:
    try:
        geometry = json.loads(filepath.read_text(encoding='utf-8'))
        if not isinstance(geometry, dict):
            raise ValueError('GeoJSON geometry must be an object')
        parsed_geometry = shape(geometry)
    except (OSError, ValueError, TypeError) as err:
        raise click.ClickException(f'Invalid GeoJSON geometry: {err}') from err

    if parsed_geometry.is_empty or not parsed_geometry.is_valid:
        raise click.ClickException('GeoJSON geometry must be non-empty and valid')
    if geometry.get('type') not in ('Point', 'Polygon'):
        raise click.ClickException('Geometry type must be Point or Polygon')
    return geometry


@click.command('publish-url')
@click.option('--url', required=True, help='Externally hosted data URL')
@click.option('--metadata-id', required=True, help='Dataset metadata identifier')
@click.option('--geometry', required=True,
              type=click.Path(exists=True, dir_okay=False, readable=True,
                              path_type=Path),
              help='Path to a GeoJSON geometry file')
@click.option('--datetime', 'datetime_', required=True,
              help='Timezone-aware ISO-8601 datetime for the data')
@cli_helpers.OPTION_VERBOSITY
def publish_url(url, metadata_id, geometry, datetime_, verbosity):
    """Publish a notification for an externally hosted data resource."""

    url = _validate_url(url)
    try:
        data_datetime = isoparse(datetime_)
    except (TypeError, ValueError) as err:
        raise click.ClickException(f'Invalid ISO-8601 datetime: {err}') from err
    if data_datetime.tzinfo is None or data_datetime.utcoffset() is None:
        raise click.ClickException('Datetime must include a timezone')
    data_datetime = data_datetime.astimezone(timezone.utc)
    data_geometry = _read_geometry(geometry)

    data_mappings = get_data_mappings()
    if metadata_id not in data_mappings:
        raise click.ClickException(
            f'metadata_id={metadata_id} not found in data mappings')

    url_path = urlsplit(url).path
    identifier = PurePosixPath(unquote(url_path)).stem
    if not identifier:
        raise click.ClickException('URL must include a filename')

    click.echo(f'Reading resource metadata from {url}')
    length, checksum_value = _read_integrity(url)
    publisher = BaseAbstractData({
        'metadata_id': metadata_id,
        'topic_hierarchy': data_mappings[metadata_id]['topic_hierarchy'],
        'notify': True
    })
    if not publisher.notify(identifier, url, data_datetime,
                            data_geometry, external_resource=True,
                            length=length, checksum_value=checksum_value):
        raise click.ClickException('Failed to publish data notification')

    click.echo(f'Published notification for {url} ({length} bytes)')