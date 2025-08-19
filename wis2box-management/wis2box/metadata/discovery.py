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

import click
from copy import deepcopy
from datetime import date, datetime
import json
import logging
import uuid
import time
from urllib.parse import urlparse

from owslib.ogcapi.records import Records
from typing import Union

from pygeometa.schemas.wmo_wcmp2 import WMOWCMP2OutputSchema
from pywcmp.errors import TestSuiteError
from pywcmp.wcmp2.ets import WMOCoreMetadataProfileTestSuite2

from wis2box import __version__
from wis2box import cli_helpers
from wis2box.api import (delete_collection_item, remove_collection,
                         setup_collection, upsert_collection_item, load_config)
from wis2box.data_mappings import refresh_data_mappings, get_plugins

from wis2box.env import (API_URL, BROKER_PUBLIC, DOCKER_API_URL,
                         STORAGE_PUBLIC, STORAGE_SOURCE, URL)
from wis2box.metadata.base import BaseMetadata
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.pubsub.message import WISNotificationMessage
from wis2box.storage import put_data, delete_data, exists
from wis2box.util import json_serial

LOGGER = logging.getLogger(__name__)


class DiscoveryMetadata(BaseMetadata):
    def __init__(self):
        super().__init__()

    def generate(self, mcf: dict) -> str:
        """
        Generate OARec discovery metadata

        :param mcf: `dict` of MCF file

        :returns: `dict` of metadata representation
        """

        md = deepcopy(mcf)

        mqtt_topic = None
        if 'wis2box' in mcf and 'topic_hierarchy' in mcf['wis2box']:
            local_topic = mcf['wis2box']['topic_hierarchy'].replace('.', '/')
            mqtt_topic = f'origin/a/wis2/{local_topic}'

            LOGGER.debug('Adding topic hierarchy')
            md['identification']['wmo_topic_hierarchy'] = local_topic
            md['identification']['wmo_data_policy'] = mqtt_topic.split('/')[5]

        LOGGER.debug('Adding revision date')
        md['identification']['dates']['revision'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')  # noqa

        LOGGER.debug('Checking temporal extents')
        if md['identification']['extents']['temporal'][0].get('begin', 'BEGIN_DATE') is None:  # noqa
            today = date.today().strftime('%Y-%m-%d')
            md['identification']['extents']['temporal'][0]['begin'] = today

        # md set 'distribution' to empty object, we add links later
        if 'distribution' not in md:
            md['distribution'] = {}

        LOGGER.debug('Generating OARec discovery metadata')
        record = WMOWCMP2OutputSchema().write(md, stringify=False)
        if mqtt_topic is not None:
            record['properties']['wmo:topicHierarchy'] = mqtt_topic

        record['wis2box'] = mcf['wis2box']

        if record['properties']['contacts'][0].get('organization') is None:
            record['properties']['contacts'][0]['organization'] = record['properties']['contacts'][0].pop('name', "NOTSET")  # noqa

        try:
            phone = record['properties']['contacts'][0]['phones'][0]['value']
            if isinstance(phone, int):
                record['properties']['contacts'][0]['phones'][0]['value'] = f'+{phone}'  # noqa
            elif not phone.startswith('+'):
                LOGGER.debug('Casting phone to string')
                record['properties']['contacts'][0]['phones'][0]['value'] = f'+{phone}'  # noqa
        except KeyError:
            LOGGER.debug('No phone number defined')

        try:
            postalcode = record['properties']['contacts'][0]['addresses'][0]['postalcode']  # noqa
            if isinstance(postalcode, int):
                record['properties']['contacts'][0]['addresses'][0]['postalcode'] = f'{postalcode}'  # noqa
        except KeyError:
            LOGGER.debug('No postal code defined')
            pass

        return record

    def get_distribution_links(self,
                               record: dict,
                               format_='mcf') -> list:
        """
        Generates distribution links

        :param record: `dict` of discovery metadata record
        :param format_: `str` of format (`mcf` or `wcmp2`)

        :returns: `list` of distribution links
        """

        LOGGER.info('Adding distribution links')

        identifier = record['id']
        topic = record['properties'].get('wmo:topicHierarchy')

        links = []
        if 'links' in record:
            for link in record['links']:
                try:
                    if link.get('title') == 'Notifications':
                        LOGGER.debug('Skipping notifications link')
                        continue
                    # links containing identifier will be added later
                    if identifier in link['href']:
                        LOGGER.debug(f'Skipping link {link["href"]}')
                        continue
                    links.append(link)
                except Exception as err:
                    LOGGER.error(f'Error processing link {link}: {err}')
                    continue

        plugins = get_plugins(record)
        # check if any plugin-names contains 2geojson
        has_2geojson = any('2geojson' in plugin for plugin in plugins)
        if has_2geojson:
            # default view is descending by reportTime
            oafeat_link = {
                'href': f'{API_URL}/collections/{identifier}/items?sortby=-reportTime', # noqa
                'type': 'application/json',
                'name': identifier,
                'description': f'Observations in json format for {identifier}',
                'rel': 'collection'
            }
            links.append(oafeat_link)

        if topic is None:
            LOGGER.info('Do not add broker link, no topic defined')
        else:
            mqp_link = {
                'href': get_broker_public_endpoint(),
                'type': 'application/json',
                'name': topic,
                'description': 'Notifications',
                'rel': 'items',
                'channel': topic
            }
            links.append(mqp_link)

        canonical_link = {
            'href': f"{API_URL}/collections/discovery-metadata/items/{identifier}",  # noqa
            'type': 'application/geo+json',
            'name': identifier,
            'description': identifier,
            'rel': 'canonical'
        }
        links.append(canonical_link)

        if format_ == 'mcf':
            for link in links:
                link['url'] = link.pop('href')

        return links


def publish_broker_message(record: dict, storage_path: str,
                           centre_id: str, operation: str = 'create') -> str:
    """
    Publish discovery metadata to broker

    :param record: `dict` of discovery metadata record
    :param storage_path: `str` of storage path/object id
    :param centre_id: centre acronym
    :param operation: `str` of operation type (create, update, delete)

    :returns: `str` of WIS message
    """

    topic = f'origin/a/wis2/{centre_id.lower()}/metadata'  # noqa

    datetime_ = datetime.strptime(record['properties']['created'], '%Y-%m-%dT%H:%M:%SZ') # noqa
    identifier = f"{centre_id.lower()}/metadata/{record['id']}"
    wis_message = WISNotificationMessage(identifier=identifier,
                                         metadata_id=None,
                                         filepath=storage_path,
                                         datetime_=datetime_,
                                         geometry=record['geometry'],
                                         operation=operation).dumps()

    # load plugin for plugin-broker
    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER_PUBLIC,
        'client_type': 'publisher'
    }
    broker = load_plugin('pubsub', defs)

    success = broker.pub(topic, wis_message)
    if not success:
        raise RuntimeError(f'Failed to publish message to {topic}')

    return wis_message


def gcm() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'discovery-metadata',
        'type': 'record',
        'title': 'Discovery metadata',
        'description': 'Discovery metadata',
        'keywords': ['wmo', 'wis 2.0'],
        'links': ['https://example.org'],
        'bbox': [-180, -90, 180, 90],
        'id_field': 'identifier',
        'time_field': 'created',
        'title_field': 'title'
    }


def publish_delete_notification(identifier: str):
    """
    Deletes a discovery metadata record from the catalogue

    :param identifier: `str` of metadata identifier

    :returns: `bool` of publishing result
    """

    LOGGER.info(f'Publishing delete notification for {identifier}')

    # check that id starts with 'urn:wmo:md:'
    if not identifier.startswith('urn:wmo:md:'):
        msg = f'Invalid WCMP2 id: {identifier}, does not start with urn:wmo:md:'  # noqa
        LOGGER.error(msg)
        raise RuntimeError(msg)
    # parse centre id from identifier
    centre_id = identifier.split(':')[3]
    topic = f'origin/a/wis2/{centre_id}/metadata'
    # prepare WIS message
    links = [{
        'href': f'{URL}/data/metadata/{identifier}',
        'rel': 'deletion',
        'title': f'Delete discovery metadata for {identifier}'
    }]
    message = {
        'id': str(uuid.uuid4()),
        'type': 'Feature',
        'conformsTo': ['http://wis.wmo.int/spec/wnm/1/conf/core'],
        'geometry': None,
        'properties': {
            'data_id': f'{centre_id}/metadata/{identifier}',
            'metadata_id': identifier,
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'pubtime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        },
        'links': links,
        'generated_by': f'wis2box {__version__}'
    }

    # load plugin for plugin-broker
    defs = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': BROKER_PUBLIC,
        'client_type': 'publisher'
    }
    broker = load_plugin('pubsub', defs)

    success = broker.pub(topic, json.dumps(message, default=json_serial))
    if success:
        try:
            upsert_collection_item('messages', message)
        except Exception as err:
            msg = f'Failed to publish message to API: {err}'
            LOGGER.error(msg)
            raise RuntimeError(msg) from err

    return success


def publish_discovery_metadata(metadata: Union[dict, str]):
    """
    Inserts or updates discovery metadata to catalogue

    :param metadata: `str` of MCF or `dict` of WCMP2

    :returns: `bool` of publishing result
    """

    setup_collection(meta=gcm())

    LOGGER.debug('Publishing discovery metadata')

    new_links = []
    if isinstance(metadata, dict):
        LOGGER.info('Adding WCMP2 record from dictionary')
        record = metadata
        dm = DiscoveryMetadata()
    else:
        LOGGER.info('Transforming MCF into WCMP2 record')
        dm = DiscoveryMetadata()
        record_mcf = dm.parse_record(metadata)
        record = dm.generate(record_mcf)

    if 'language' in record['properties']:
        _ = record['properties'].pop('language')

    distribution_links = dm.get_distribution_links(record, format_='wcmp2')
    # update links, do not extend or we get duplicates
    record['links'] = distribution_links
    for link in record['links']:
        if 'description' in link:
            link['title'] = link.pop('description')
        if 'url' in link:
            link['href'] = link.pop('url')

    if 'x-wmo' in record['id']:
        msg = 'Change x-wmo to wmo in metadata identifier'
        LOGGER.error(msg)
        raise RuntimeError(msg)

    if 'data_mappings' not in record['wis2box']:
        msg = 'Missing wis2box.data_mappings definition'
        LOGGER.error(msg)
        raise RuntimeError(msg)

    LOGGER.info('Checking if record / auth enabled')
    oar = Records(DOCKER_API_URL)
    try:
        records = oar.collection_items('discovery-metadata')
        # find record in existing records
        r = next((r for r in records['features'] if r['id'] == record['id']), None) # noqa
        if r is None:
            LOGGER.debug('Record not found in existing records')
        elif r['wis2box'].get('has_auth', False):
            LOGGER.debug('Auth enabled, adding to record')
            record['wis2box']['has_auth'] = True
        else:
            LOGGER.debug('No auth defined')
    except Exception:
        LOGGER.error('Failed to check for auth')

    # TODO: remove at some point
    try:
        resolution = record['time']['resolution']
        if not resolution.startswith('PT') and resolution.endswith('H'):
            resolution2 = resolution.replace('P', 'PT')
            LOGGER.warning(f'Incorrect time resolution detected: adjusting time.resolution {resolution} to {resolution2}')  # noqa
            record['time']['resolution'] = resolution2
    except KeyError:
        pass

    LOGGER.debug('Publishing to API')
    try:
        upsert_collection_item('discovery-metadata', record)
    except Exception as err:
        msg = f'Failed to publish discovery metadata: {err} content: {record}'  # noqa
        LOGGER.error(msg)
        # avoid crashing the whole process
        return

    LOGGER.debug('Removing internal wis2box metadata')
    record.pop('wis2box')
    record['properties'].pop('wmo:topicHierarchy', None)

    LOGGER.debug('Sanitizing links')
    if 'links' in record:
        old_links = record.pop('links')

    for ol in old_links:
        if API_URL not in ol['href']:
            new_links.append(ol)

    record['links'] = new_links

    LOGGER.info(f'Validating WCMP2 record {record["id"]}')
    try:
        ts = WMOCoreMetadataProfileTestSuite2(record)
        _ = ts.run_tests(fail_on_schema_validation=True)
        ts.raise_for_status()
    except TestSuiteError as err:
        # if the only error is about the WIS2 topic, continue with publishing
        if len(err.errors) == 1 and 'message' in err.errors[0] and err.errors[0]['message'] == 'Invalid WIS2 topic (unknown centre-id) for Pub/Sub link channel': # noqa
            LOGGER.warning(f"{err.errors[0]['message']} continuing with publishing")  # noqa
        else:
            msg = 'Metadata invalid, WCMP2 validation errors: ' + ', '.join([err['message'] for err in err.errors])	 # noqa
            LOGGER.error(msg)
            raise RuntimeError(msg)

    LOGGER.debug('Saving to object storage')
    data_bytes = json.dumps(record,
                            default=json_serial).encode('utf-8')
    storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{record['id']}.json"  # noqa

    operation = 'update' if exists(storage_path) else 'create'
    put_data(data_bytes, storage_path, 'application/geo+json')

    # if 2geojson add data-collection
    plugins = get_plugins(record)
    # check if any plugin-names contains 2geojson
    has_2geojson = any('2geojson' in plugin for plugin in plugins)
    if has_2geojson:
        api_config = load_config()
        api_collections = api_config.list_collections()
        metadata_id = record['id']
        # check if metadata_id is in api_collections
        if metadata_id not in api_collections:
            LOGGER.info(f'Adding data-collection for: {metadata_id}')
            try:
                from wis2box.data import gcm as data_gcm
                meta = data_gcm(record)
                setup_collection(meta=meta)
            except Exception as err:
                LOGGER.error(f'ERROR adding data-collection for: {metadata_id}: {err}') # noqa

    LOGGER.debug('Publishing message')
    # check that id starts with 'urn:wmo:md:'
    if not record['id'].startswith('urn:wmo:md:'):
        msg = f'Invalid WCMP2 id: {record["id"]}, does not start with urn:wmo:md:'  # noqa
        LOGGER.error(msg)
        raise RuntimeError(msg)
    # parse centre id from identifier
    centre_id = record['id'].split(':')[3]
    try:
        message = publish_broker_message(record, storage_path,
                                         centre_id, operation)
    except Exception as err:
        msg = 'Failed to publish discovery metadata to public broker'
        LOGGER.error(msg)
        raise RuntimeError(msg) from err
    try:
        upsert_collection_item('messages', json.loads(message))
    except Exception as err:
        msg = f'Failed to publish message to API: {err}'
        LOGGER.error(msg)
        raise RuntimeError(msg) from err

    return


def get_broker_public_endpoint() -> str:
    """
    Helper function to use WIS2BOX_URL to create a publically accessible
    broker endpoint
    """

    url_parsed = urlparse(URL)

    if url_parsed.scheme == 'https':
        scheme = 'mqtts'
        port = 8883
    else:
        scheme = 'mqtt'
        port = 1883

    return f'{scheme}://everyone:everyone@{url_parsed.hostname}:{port}'


@click.group('discovery')
def discovery_metadata():
    """Discovery metadata management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def setup(ctx, verbosity):
    """Initializes metadata repository"""

    click.echo('Setting up discovery metadata repository')
    setup_collection(meta=gcm())


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def republish(ctx, verbosity):
    """Republish all published discovery metadata"""

    # read existing records
    oar = Records(DOCKER_API_URL)
    try:
        records = oar.collection_items('discovery-metadata')
    except Exception as err:
        click.echo(f'Could not retrieve records: {err}')

    for record in records['features']:
        click.echo(f'Republishing {record["id"]}')
        try:
            publish_discovery_metadata(record)
            click.echo(f'Successfully republished {record["id"]}')
        except Exception:
            click.echo(f'Failed to publish {record["id"]}')


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        publish_discovery_metadata(filepath.read())
    except Exception as err:
        raise click.ClickException(f'Failed to publish: {err}')
    refresh_data_mappings()
    time.sleep(1)
    refresh_data_mappings()
    click.echo('Discovery metadata published')


@click.command()
@click.pass_context
@click.argument('identifier')
@click.option('--force', '-f', default=False, is_flag=True,
              help='Force delete associated data from API')
@cli_helpers.OPTION_VERBOSITY
def unpublish(ctx, identifier, verbosity, force=False):
    """Deletes a discovery metadata record from the catalogue"""

    click.echo(f'Un-publishing discovery metadata {identifier}')
    try:
        publish_delete_notification(identifier)
    except click.ClickException as err:
        click.echo(f'Failed to send delete notification: {err}')
        return
    click.echo(f'Successfully sent delete notification for {identifier}')

    try:
        delete_collection_item('discovery-metadata', identifier)
    except Exception:
        raise click.ClickException('Metadata identifier not present in local discovery catalogue') # noqa
    refresh_data_mappings()
    time.sleep(1)
    refresh_data_mappings()
    click.echo('Discovery metadata unpublished')

    if force:
        click.echo('Deleting associated data from the API')
        remove_collection(identifier)
        click.echo('Removing data from object storage')
        storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{identifier}.json" # noqa
        try:
            delete_data(storage_path)
        except Exception:
            raise click.ClickException('Failed to remove data from object storage') # noqa


discovery_metadata.add_command(publish)
discovery_metadata.add_command(setup)
discovery_metadata.add_command(unpublish)
discovery_metadata.add_command(republish)
