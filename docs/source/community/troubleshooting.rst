.. _troubleshooting:

Troubleshooting
===============

This page lists several commonly seen issues and how to address them.

wis2box-ctl.py status: one or more containers are restarting
------------------------------------------------------------

When executing the command ``python3 wis2box-ctl.py status``, showing one or more services as restarting or unhealthy, they are failing to start.

If services are not running at all (status shows exited or not running), start them: 

.. code-block:: bash

   python3 wis2box-ctl.py start

If services are restarting/unhealthy, check the logs to identify the cause.

If Grafana is running: 

You can use the 'Explore' option in Grafana running on port 3000 of your instance to view the logs of the wis2box services. Open a browser and navigate to ``http://<your-instance-ip>:3000``.  Select 'Explore' from the menu on the left,
then select 'wis2box-loki' as the datasource and use ``label=container_name`` as illustrated in the image below:

.. image:: ../_static/troubleshooting_grafana.png
   :alt: Explore option in Grafana
   :width: 1000
   :align: center

Select the ``container_name`` for the service you want to inspect, click on the 'Run query' button and scroll down to view the logs.

If Grafana is not accessible:

Check logs directly from the host:

.. code-block:: bash

   docker compose logs --tail=200 <container_name> 

Common causes: 

1. Port in use, for example check if port 80 is already used by existing apache/httpd service 

2. WIS2BOX_STORAGE_PASSWORD too short (MinIO fails to start)  

3. WIS2BOX_BROKER_PASSWORD contains @ 

4. Missing required files (e.g., metadata/station/station_list.csv) 

5. Insufficient disk space (df -h) 

After fixing the issue, restart all services: 

.. code-block:: bash

   python3 wis2box-ctl.py stop
   python3 wis2box-ctl.py start

No station on map in wis2box-ui
-------------------------------

The stations displayed in the wis2box-ui per dataset are defined by the topic associated with the station. If the topic for this dataset has no stations associated to it, you will get this pop-up:

.. image:: ../_static/troubleshooting_no_station_pop_up.png
   :alt: No Station pop up
   :width: 1000
   :align: center
   
To associate a station with a topic, you can edit the station metadata using the station editor in wis2box-webapp or you can use the command wis2box metadata station add-topic to add a topic to a station. See documentation section of adding stations.

The Access Key Id you provided does not exist in our records
------------------------------------------------------------

If you see this error when uploading data to the wis2box-incoming storage, you have provided the wrong username and/or password to access MinIO.
Check the values for ``WIS2BOX_STORAGE_USERNAME`` and ``WIS2BOX_STORAGE_PASSWORD`` set in the ``wis2box.env`` file.

ERROR - Failed to publish, wsi: ..., tsi: XXXXX
-----------------------------------------------

Data arrived for a station that is not present in the station metadata cache. 

Use the ``station editor`` in ``wis2box-webapp`` to add the missing station and associate it with the correct topic hierarchy.

.. image:: ../_static/wis2box-webapp-stations.png
   :alt: Station
   :width: 1000
   :align: center

After saving, the cache is refreshed and the station becomes available to pipelines.

wis2box UI connection error
---------------------------

If when you access the wis2box UI you see the interface but no datasets are visible; check the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` are set correctly.

If when you access the wis2box UI you see a TypeError: Failed to fetch error
This indicates that the UI could not connect to the wis2box API：

.. image:: ../_static/wis2box-webapp-dataset_failed_to_fetch.png
   :alt: Fail to Fetch
   :width: 1000
   :align: center

Check that:

1. WIS2BOX_API_URL in your configuration points to the correct API endpoint (including protocol, host, and port).

2. The wis2box API service is running and accessible from your browser.

3. Any reverse proxy or firewall is correctly forwarding requests to the API.

4. After correcting the configuration, restart wis2box for the changes to take effect.

wis2box-ui is empty
-------------------
If when you access the wis2box UI you see the interface but no datasets are visible, and a message appears saying ``Discovery Metadata contains no datasets``

.. image:: ../_static/wis2box-webapp-dataset_empty.png
   :alt: UI empty
   :width: 1000
   :align: center

Open the wis2box-webapp, add a new dataset, and configure the required fields such as the topic hierarchy and etc. Save the dataset to make it visible in the UI.
