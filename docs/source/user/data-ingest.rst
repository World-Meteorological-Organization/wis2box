.. _data-ingest:

Ingesting data for publication
==============================

In WIS2, the availability of new data to be downloaded is announced using WIS2 Notifications sent using the MQTT protocol.
Each WIS2 Notification will contain a "canonical" URL to the data to enable the data to be downloaded over HTTP(S).

The *wis2box-management* service listens to updates from the *wis2box-storage*-service about new files received and will attempt to process the files based on the datasets and data mappings that have been configured in the previous section.

The *wis2box-storage* service is based on `MinIO`_ , the following buckets are pre-configured when the wis2box-stack is started for the first time:

- **wis2box-incoming**: this bucket is used to received incoming files and are used as input by the data mappings configured in your wis2box
- **wis2box-public**: this bucket is used to store files to be shared on WIS2, it is proxied by the web-proxy service to make it available over HTTP(S) at `WIS2BOX_URL/data/`

.. note::
 
 If you use "CSV to BUFR" plugin in your data mappings, the columns defined in the input CSV file must match the columns defined by the `csv2bufr-template`. 
 If the columns do not match, the data will not be processed and an error will be raised in the logs of the *wis2box-management* container.
 
 See the :ref:`csv2bufr-plugin` for more information on this data plugin and see the `csv2bufr-templates`_ repository for the template definitions.

.. note::

  If you use "FM-12 to BUFR" (synop2bufr) plugin in your data mappings, your filename must contain a year and month, and the year and month should match the 1st and 2nd group in your regex.

  See the :ref:`synop2bufr-plugin` for more information.

**For production use, it is recommended to setup an automated workflow and to regularly review the data publication workflow in the Grafana-service.**

Data ingest methods
-------------------

.. toctree::
   :maxdepth: 1

   data-ingest/webapp-manual-ingestion
   data-ingest/minio-scripts
   data-ingest/minio-sftp
   data-ingest/Moving-Weather
   data-ingest/CDMS-SURFACE
   data-ingest/CDMS-ClimSoft
   data-ingest/CDMS-CLIDE
   data-ingest/tools-ADL
   data-ingest/campbell-mqtt

Testing and monitoring
----------------------

.. toctree::
   :maxdepth: 1

   test-and-monitor/minio-console
   test-and-monitor/workflow-monitoring

Next steps
----------

After you have successfully setup your data ingest process into the wis2box, you are ready to share your data with the global
WIS2 network by enabling external access to your public services.

Next: :ref:`public-services-setup`

.. _`MinIO`: https://github.com/world-Meteorological-Organization/wis2box-minio
.. _`csv2bufr-templates`: https://github.com/World-Meteorological-Organization/csv2bufr-templates
