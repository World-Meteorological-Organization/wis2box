.. _setup-datasets:


Adding datasets and discovery metadata
======================================

Datasets in the wis2box are required to define the **discovery metadata** and **data mappings plugins** for data you want to publish:

- **Discovery metadata**: dataset properties such as title, description, keywords, and bounding box used to create a WIS Control Metadata Profile (WCMP2) record for the dataset.
- **Data mappings plugins**: define the actions to be performed on the data before it is published, such as transforming the data from the input source format and validating the data content.

For each dataset you create, a new WCMP2 record will be created and made available in the HTTP storage of your wis2box instance.
The wis2box-broker will publish a WIS2 data notification for the WCMP2 record at the topic `origin/a/wis2/CENTRE_ID/metadata`, where `CENTRE_ID` is the centre-id of the dataset.
This metadata-notification enables the WIS2 Global Discovery Catalogue to download and cache the metadata record, allowing users to discover the dataset when searching the WIS2 Global Discovery Catalogue.

The following sections will explain how to create datasets in your wis2box using the wis2box-webapp.

Accessing the wis2box-webapp
----------------------------

You can access the wis2box-webapp by visiting the URL you specified during the configuration step in your web browser and adding ``/wis2box-webapp`` to the URL.
For example, if you specified ``http://mywis2box.example.com`` as the URL, you can access the wis2box-webapp by visiting ``http://mywis2box.example.com/wis2box-webapp``.

You can check the WIS2BOX_URL environment variable in the ``wis2box.env`` file to find the URL of your wis2box instance:

.. code-block:: bash

   cat wis2box.env | grep WIS2BOX_URL

The wis2box-webapp used basic authentication to control access to the webapp.  The default username is ``wis2box-user`` and the password is the value specified when running the script ``wis2box-create-config.py``.

The values of ``WIS2BOX_WEBAPP_USERNAME`` and ``WIS2BOX_WEBAPP_PASSWORD`` can be found in the ``wis2box.env`` file as follows:

.. code-block:: bash

   cat wis2box.env | grep WIS2BOX_WEBAPP_USERNAME
   cat wis2box.env | grep WIS2BOX_WEBAPP_PASSWORD

.. _adding-datasets:

Adding datasets
---------------

Open the wis2box-webapp in your web browser, provide the WIS2BOX_WEBAPP credentials, and select the **dataset editor** from the menu on the left

You should see the following page:

.. image:: ../_static/wis2box-webapp-dataset_editor.png
  :width: 1000
  :alt: wis2box webapp dataset editor page

To create a new dataset select "Create new" from the dataset editor page.

A popup will appear where you can define your *"centre-id"* and the *"Template"* of dataset you want to create:

.. image:: ../_static/wis2box-webapp-dataset_editor_continuetoform.png
  :width: 600
  :alt: wis2box webapp dataset editor page, continue to form

.. note::

   Your centre-id should start with the ccTLD of your country, followed by a - and an abbreviated name of your organization, for example ``fr-meteofrance``.
   The centre-id has to be lowercase and use alphanumeric characters only.
   **To define a new centre-id type the centre-id into the box**, otherwise select one from the dropdown list.
   The dropdown list shows all currently registered centre-ids on WIS2 as well as any new centre-ids for datasets created in your wis2box-instance.

You have the option to select a *Template*, such as "weather/surface-based-observations/synop", "weather/surface-based-observations/temp", and "weather/advisories-warnings".
The templates help you to predefine some of the metadata properties and the data mappings plugins for commonly published data-types.

If you don't want to use a template, or your dataset does not fit into one of the predefined templates, select "Other" from the dropdown list.

Please select "Continue to form" to start defining your dataset.

When defining your dataset, you will need to specify a Local ID, which serves as a short and unique identifier for the dataset within your organization. The Local ID is used to generate the WCMP2 identifier for your metadata record.

.. image:: ../_static/wis2box-webapp-dataset_editor_local_id.png
  :width: 800
  :alt: wis2box webapp dataset editor page, localID

.. note::

   If you do not provide a Local ID a randomly generated ID will be assigned. It is strongly suggested to define your own human-readable ID instead. Once the dataset is created, the Local ID cannot be changed. To use a different Local ID, you will need to delete and recreate the dataset.

Make sure to provide a "description" for your dataset, review and add keywords and choose an appropriate bounding box.
You will also need to provide some contact information for the dataset.

Before publishing the new dataset make to click "Validate form" to check if all required fields are filled in:

.. image:: ../_static/wis2box-webapp-dataset_editor_validateform.png
  :width: 1000
  :alt: wis2box webapp dataset editor page, validate form

Each dataset is associated with data-mappings plugins that transform the data from the input source format before the data is published.
If you are using the predefined dataset types for "synop", "temp", or CAP alert data, the data mappings plugins will be predefined for you.
Otherwise, you will need to define the data mappings plugins for your dataset.

Finally, click "submit" to publish the dataset:

.. image:: ../_static/wis2box-webapp-dataset_editor_success.png
  :width: 800
  :alt: wis2box webapp dataset editor page, submit

.. note::

   You can also create datasets by defining MCF files in the ``metadata/discovery`` directory in your wis2box host directory and publish them from the CLI.
   For more information on publishing datasets using MCF files, see the reference documentation.

Next steps
----------

The next step is to associate stations to the dataset you have created, see :ref:`setup-stations`.

.. _`WIS2 topic hierarchy`: https://github.com/World-Meteorological-Organization/wis2-topic-hierarchy
