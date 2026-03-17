.. _tools-ADT:

Using ADT by IRI/SEI
====================

The `Automatic Weather Station Data Tool (ADT) <https://iri.columbia.edu/our-expertise/climate/tools/adt/>`_ is a web-based application developed by the International Research Institute for Climate and Society (IRI) that
enables NMS to access, process, quality control, analyze, visualize, and disseminate data from different AWS systems in one place.

The ADT provides an API enabling you to extract data and forward it to wis2box for publication on WIS2. 

See below for an example of how to use Python to extract data from the ADT API and send it to your wis2box instance using the MinIO client library for Python:

.. code-block:: python

    import requests
    from minio import Minio

    # NEED EXAMPLE CODE FROM IRI/SEI ON HOW TO EXTRACT DATA FROM ADT API
