.. _troubleshooting:

Troubleshooting
===============

This page lists common issues encountered and how to address them accordingly.

Permission denied after executing "python3 wis2box-ctl.py start"
----------------------------------------------------------------

The ``wis2box-ctl.py`` utility is a Python script which manages using Docker commands in a convenient manner.  When running
``python3 wis2box-ctl.py start``, if there is a permission denied error, 
it is likely that the user running this command does not have the required permissions to run Docker commands.

To fix this, make sure to add your user to the ``docker`` group:

.. code-block:: bash

    sudo usermod -aG docker $USER
    # logout and login for changes to take effect

Bind for 0.0.0.0:XX failed: port is already allocated
-----------------------------------------------------

wis2box includes a set of services that bind to specific ports on the host system.

Make sure that the ports required on the host are available see :ref:`getting-started` for the list of ports used by wis2box.

If you are unsure which process is using a specific port, you can try to check using one of the following commands:

.. code-block:: bash

    sudo lsof -i :80   # Find process using port 80
    sudo netstat -tuln # Alternative check

wis2box-ctl.py status: one or more containers are restarting
------------------------------------------------------------

If the output of the command ``python3 wis2box-ctl.py status`` displays one or more services as restarting or unhealthy, 
they are likely failing to start due to an error in the configuration or insufficient resources resulting in a failed startup.

If services are not running at all (status shows exited or not running), start them as follows:

.. code-block:: bash

   python3 wis2box-ctl.py start

Please check for Docker issues as described above during the startup process.

If services are restarting/unhealthy, check the logs to identify the cause.

If Grafana is running: 

You can use the 'Explore' option in Grafana running on port 3000 of your instance to view the logs of the wis2box services. Open a browser and navigate to ``http://<your-instance-ip>:3000``.  Select 'Explore' from the menu on the left,
then select 'wis2box-loki' as the datasource and use ``label=container_name`` as illustrated in the image below:

.. image:: ../_static/troubleshooting_grafana.png
   :alt: Explore option in Grafana
   :width: 1000
   :align: center

Select the ``container_name`` for the service to be inspected, click on the 'Run query' button and scroll down to view the logs.

If Grafana is not accessible:

Check logs directly from the host:

.. code-block:: bash

   docker compose logs --tail=200 <container_name> 

Please check the logs for the following containers:

- `wis2box-management`
- `wis2box-minio`
- `wis2box-api`
- `elasticsearch`
- `mosquitto`

Common causes: 

1. ``WIS2BOX_STORAGE_PASSWORD`` is too short (MinIO fails to start, edit `wis2box.env` and set a longer password)  

2. ``WIS2BOX_BROKER_PASSWORD`` contains the ``@`` character (broker authentication fails, edit `wis2box.env` and set a password without ``@``)

3. Insufficient disk space (Use ``df -h`` to check disk space)

4. Docker volumes present from an older wis2box installation (use ``docker volume ls`` to list volumes and ``docker volume rm <volume_name>`` to remove them)

After fixing the issue, restart all services: 

.. code-block:: bash

   python3 wis2box-ctl.py stop
   python3 wis2box-ctl.py start

No station on map in wis2box-ui
-------------------------------

The stations displayed in the wis2box-ui per dataset are defined by the topic associated with the station. If the topic for this dataset has no stations associated to it, you will get the following popup:

.. image:: ../_static/troubleshooting_no_station_pop_up.png
   :alt: No Station popup
   :width: 1000
   :align: center
   
Consult the user guide for instructions on how to manage the stations in the wis2box-webapp.

The Access Key Id you provided does not exist in our records
------------------------------------------------------------

If this error occurs when uploading data to the wis2box-incoming storage, the username/password credentials for MinIO access are incorrect.

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

If the wis2box UI is available but no datasets are visible, check the ``WIS2BOX_URL`` and ``WIS2BOX_API_URL`` are set correctly.

If error ``TypeError: Failed to fetch error`` appears in the wis2box UI, this indicates that the UI could not connect to the wis2box API：

.. image:: ../_static/wis2box-webapp-dataset_failed_to_fetch.png
   :alt: Fail to Fetch
   :width: 1000
   :align: center

Verify that:

1. ``WIS2BOX_API_URL`` in configuration points to the correct API endpoint (including protocol, host, and port).

2. The wis2box API service is running and accessible from a web browser.

3. Any reverse proxy or firewall is correctly forwarding requests to the API.

4. After correcting the configuration, restart wis2box for the changes to take effect.

wis2box UI is empty
-------------------

If the wis2box UI is available but no datasets are visible, and the message ``Discovery Metadata contains no datasets`` is displayed:

.. image:: ../_static/wis2box-webapp-dataset_empty.png
   :alt: UI empty
   :width: 1000
   :align: center

This means the collection ``discovery-metadata`` in the wisbox API is empty, due to no datasets having been created or Docker volume ``wis2box_project_es-data`` was removed.

Consult the user guide for instructions on creating datasets.

Elasticsearch not starting: "java.lang.OutOfMemoryError: Java heap space"
-------------------------------------------------------------------------

If you notice Elasticsearch failing to start and the logs contain the message ``java.lang.OutOfMemoryError: Java heap space``, 
this indicates that the Elasticsearch container does not have enough memory allocated to it.

You can edit the Edit the Elasticsearch configuration in ``docker-compose.yml`` to increase the memory assigned to Elasticsearch as follows:

First stop the wis2box-stack:

.. code-block:: bash

   python3 wis2box-ctl.py stop

Then edit docker-compose.yml and replace:

.. code-block:: yaml

   - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

with:

.. code-block:: yaml

   - "ES_JAVA_OPTS=-Xms1g -Xmx1g"

and also  replace:

.. code-block:: yaml

   mem_limit: 1.5g
   memswap_limit: 1.5g

with:

.. code-block:: yaml

   mem_limit: 2g
   memswap_limit: 2g

Then start the wis2box-stack again:

.. code-block:: bash

   python3 wis2box-ctl.py start

Make sure that your host has enough free memory for the new settings.

MinIO unable to start SFTP server to sftp id_rsa missing
---------------------------------------------------------

When the following error appears in the logs of the `wis2box-minio` container:

.. code-block:: bash

   FATAL unable to start SFTP server: invalid arguments passed, private key file is not accessible: open /home/miniouser/.ssh/id_rsa: no such file or directory

It means that the SSH keys required to start the SFTP server are missing.

If you used the `wis2box-create-config.py` script to create your configuration files, the SSH keys are generated automatically in the directory `.ssh` inside the directory defined by `WIS2BOX_HOST_DATADIR` (from wis2box-1.2)

If required, manually create the SSH keys as follows:

.. code-block:: bash

   mkdir -p <your-wis2box-host-datadir>/.ssh
   ssh-keygen -t rsa -b 4096 -f <your-wis2box-host-datadir>/minio/.ssh/id_rsa -N "" -q

Make sure to replace ``<your-wis2box-host-datadir>`` with the actual path defined by ``WIS2BOX_HOST_DATADIR`` in `wis2box.env`.

SFTP support in MinIO can be disabled to allow wis2box to start without SSH keys. Data ingest via SFTP will not be possible as a result.

To do so, first stop wis2box:

.. code-block:: bash

   python3 wis2box-ctl.py stop

Then edit ``docker-compose.yml`` and replace:

.. code-block:: yaml

   command: server --quiet --console-address ":9001" --sftp="address=:8022" --sftp="ssh-private-key=/home/miniouser/.ssh/id_rsa" /data

With:

.. code-block:: yaml

   command: server --quiet --console-address ":9001" /data

After making the changes, start wis2box again:

.. code-block:: bash

   python3 wis2box-ctl.py start

And check if the all the services are now running as expected:

.. code-block:: bash

   python3 wis2box-ctl.py status
