.. _setup-stations:

Adding station metadata
=======================

The following plugins rely on information provided via station metadata configured in wis2box:

- BUFR data converted to BUFR
- FM-12 data converted to BUFR
- CSV data converted to BUFR

Station configuration is required to publish data using these plugins.  Stations can be added interactively using the wis2box-webapp or by bulk inserting stations from a CSV file.

To bulk insert station metadata from a CSV file, please refer to the `Bulk inserting stations from CSV`_ section.

Creating a token for updating stations
--------------------------------------

Before proceeding, prepare an authentication token to allow updating the stations collection in wis2box.

To create a token for updating stations:

.. code-block:: bash

   wis2box auth add-token --path collections/stations

Record the token value displayed in the output of the command above. This token will be used to update stations in the next section.

Logout of wis2box-management container:

.. code-block:: bash

   exit

Adding stations using the wis2box-webapp
----------------------------------------

Go to the wis2box-webapp at *WIS2BOX_URL/wis2box-webapp/*  in a web browser.

Login with ``WIS2BOX_WEBAPP_USERNAME`` and ``WIS2BOX_WEBAPP_PASSWORD`` as defined in ``wis2box.env``.

The station editor can be accessed in the wis2box-webapp by selecting "Stations" from the menu on the left.

.. image:: ../_static/wis2box-webapp-stations.png
  :width: 800
  :alt: wis2box webapp stations page

Select "Create new" to start adding a new station.

Provide a WIGOS station identifier that will be used to import information about the station from OSCAR:

.. image:: ../_static/wis2box-webapp-stations-search.png
  :width: 800
  :alt: wis2box webapp station editor page, import station from OSCAR

Search for the station in OSCAR by providing the WIGOS station identifier and clicking "search".

If the station is found a new form will be displayed with the station information.

If the station is not found, the station form can be completed manually.

Check the form for any missing information.

Select a WIS2 topic to associate the station with.

The station editor will show the available topics to choose from based on the datasets created.

If a suitable topic is not available, it will be required to first create a dataset for that topic.

To store the station metadata, click "save" and provide the ``collections/stations`` token created in the previous section:

.. image:: ../_static/wis2box-webapp-stations-save.png
  :width: 800
  :alt: wis2box webapp station editor page, submit


Bulk inserting stations from CSV
--------------------------------

A station list CSV can be used to bulk load stations, by defining the stations in ``mystations.csv`` in the wis2box host directory and running the following command:

.. code-block:: bash

   python3 wis2box-ctl.py login
   wis2box metadata station publish-collection --path /data/wis2box/mystations.csv --topic-hierarchy origin/a/wis2/mw-mw_met_centre-test/data/core/weather/surface-based-observations/synop

.. note::

   The ``path`` argument refers to the path of the CSV file within the wis2box-management container.

   The directory defined by ``WIS2BOX_HOST_DATADIR`` is mounted as ``/data/wis2box`` in the wis2box-management container.

   The ``topic-hierarchy`` argument refers to the WIS2 topic hierarchy to associate the stations with.

After doing a bulk insert, review the stations in wis2box-webapp to ensure the stations were imported correctly.

Next steps
----------

The next step is to prepare data ingestion into wis2box, see :ref:`data-ingest`.

.. _`WIS2 topic hierarchy`: https://codes.wmo.int/wis/topic-hierarchy
.. _`OSCAR`: https://oscar.wmo.int/surface
