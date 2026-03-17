.. _campbell-mqtt:

Using CR1000X over MQTT
=======================

`CR1000X data loggers <https://www.campbellsci.com/cr1000x>`_ can be used to send a data-extract over MQTT to the wis2box broker and from there into the `wis2box-incoming` bucket.

.. note::

   This data ingestion work-flow was originally developed for selected countries in Africa as part of the WIS2 pilot in 2021.

The following steps are required to enable the ingestion of data from CR1000X data loggers over MQTT into wis2box:

- The wis2box data-plugin must use csv2bufr with the `"CampbellAfrica-v1-template" <https://github.com/World-Meteorological-Organization/csv2bufr-templates/blob/main/templates/CampbellAfrica-v1-template.json>`_ (a.k.a. "WIS2-pilot-template-2021").
- The data-loggers need to be configured to send data over MQTT to the broker endpoint in the wis2box instance.
- An additional Docker service, ``wis2box-data-subscriber``, needs to be started to parse the messages and upload the CSV files into the ``wis2box-incoming`` bucket.

You need to add an additional environment variable in your wis2box.env file to define the centre ID for which the data is being ingested, for example:

.. code-block:: none

   CENTRE_ID=<your-centre-id>

.. note::

   The data-subscriber service will upload data into the wis2box-incoming bucket in the folder:

   ``<centre-id>/data/core/weather/surface-based-observations/synop/``

   where <centre-id> is the value defined in the CENTRE_ID environment variable in your wis2box.env file.

To start the data-subscriber service, run the following docker compose command:

.. code-block:: none

   docker compose --env-file wis2box.env -f docker-compose.data-subscriber.yml up -d

Check the logs of the "wis2box-data-subscriber" container to verify the data is correctly received and forwarded to the `wis2box-incoming` bucket.

Example of logs:

.. code-block:: none

   INFO:wis2box-data-subscriber:Message received on topic=data-incoming/zmb/campbell-v1/0-894-2-NWZA001/data/cr1000x/49622/SYNOP.
   INFO:wis2box-data-subscriber:Upload csv to endpoint=localhost:9000
   INFO:wis2box-data-subscriber:Successfully uploaded zm-zmd/data/core/weather/surface-based-observations/synop/CR1000X_49622_20250805T185500Z.csv to wis2box-incoming

This service subscribes to the topic ``data-incoming/#`` on the wis2box broker and parses the content of received messages and publishes the result in the ``wis2box-incoming`` bucket.

See the GitHub `wis2box-data-subscriber`_ repository for more information on this service.

.. _`wis2box-data-subscriber`: https://github.com/wmo-im/wis2box-data-subscriber