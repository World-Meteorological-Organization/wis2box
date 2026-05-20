.. _discovery-metadata:


Discovery metadata
==================

Discovery metadata describes a given dataset or collection. Data being published through a wis2box
requires discovery metadata (describing it) to be created, maintained and published to the wis2box
catalogue API.

wis2box supports managing discovery metadata using the WMO Core Metadata Profile (WCMP2) standard.

Creating a discovery metadata record in wis2box is as easy as completing a YAML configuration file. wis2box
leverages the `pygeometa`_ project's `metadata control file (MCF)`_ format. Below is an example MCF file.


.. literalinclude:: ../../../../tests/data/metadata/discovery/mw-surface-weather-observations.yml
   :language: yaml

.. note::

   There are no strict rules for the MCF filename, although a file extension convention of ``mcf.yml`` is recommended.
   The filename does not get used/exposed or published.
   It is up to the user to determine the best filename, keeping in mind your wis2box system may manage
   and publish numerous datasets (and MCF files) over time.

.. _`pygeometa`: https://geopython.github.io/pygeometa
.. _`metadata control file (MCF)`: https://geopython.github.io/pygeometa/reference/mcf

.. _data-mappings:

Data mappings
-------------

A discovery metadata configuration file (MCF) has a `wis2box` section which provides a default data mapping (in YAML format).

The data mappings are indicated by the ``wis2box.data_mappings`` keyword, with each topic having a separate entry specifying:

- ``plugins``: all plugin objects associated with the topic, by file type/extension

Each plugin is based on the file extension to be detected and processed, with the following configuration:

- ``plugin``: the codepath of the plugin
- ``notify``: whether the plugin should publish a data notification
- ``template``: additional argument allowing a mapping template name to be passed to the plugin.  Note that if the path is relative, the plugin must be able to locate the template accordingly
- ``file-pattern``: additional argument allowing a file pattern to be passed to the plugin
- ``buckets``: the name(s) of the storage bucket(s) that data should be saved to (See :ref:`configuration` for more information on buckets)

See :ref:`extending-wis2box` for more information on adding your own data processing
pipeline.

Geometry and dateline crossing
-----------------------------

For datasets whose geometries cross the international dateline, an MCF file can be updated to support additional geometries as a MultiPolygon (i.e. splitting the dataset geometry into two bounding box polygons, by the dateline).

Below is an example of updating an MCF file with two geometries, using the country of New Zealand:

.. code:: yaml

   extents:  # split of [164, -53.8, -174.1, -27.8]
       spatial:
           - bbox: [164.1, -53.8, 180, -27.8]
             crs: 4326
           - bbox: [-180, -53.8, -174.1, -27.8]
             crs: 4326

.. note::

   Dateline crossing functionality is only currently supported when publishing discovery metadata via MCF files and the wis2box command line.  Functionality is `planned`_ for managing dateline crossing datasets in the dataset editor as part of a future release.



Summary
-------

At this point, you have created discovery metadata for your given dataset(s).

.. _planned: https://github.com/World-Meteorological-Organization/wis2box/issues/1091
