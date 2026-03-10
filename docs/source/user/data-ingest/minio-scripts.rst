
.. _minio-scripts:

Using custom scripts
====================

To automate the data ingest process, you can prepare scripts using the MinIO client libraries.
As MinIO is compatible with the S3 API, any S3 client library can be used to upload data to MinIO.

See below a Python example to upload data using the MinIO library for Python:

.. code-block:: python

    import glob
    import sys

    from minio import Minio

    filepath = '/home/wis2box-user/local-data/mydata.bin'
    # path should match the metadata or the topic in the data mappings
    minio_path = 'urn:wmo:md:it-meteoam:surface-weather-observations'

    endpoint = 'http://localhost:9000'
    WIS2BOX_STORAGE_USERNAME = 'wis2box'
    WIS2BOX_STORAGE_PASSWORD = '<your-wis2box-storage-password>'

    client = Minio(
        endpoint=endpoint,
        access_key=WIS2BOX_STORAGE_USERNAME,
        secret_key=WIS2BOX_STORAGE_PASSWORD,
        secure=False)
    
    filename = filepath.split('/')[-1]
    client.fput_object('wis2box-incoming', minio_path+filename, filepath)

.. note::
    
    In the example the file ``mydata.bin`` in ingested from the directory ``/home/wis2box-user/local-data/`` on the host running wis2box.
    If you are running the script on the same host as wis2box, you can use the endpoint ``http://localhost:9000`` as in the example. 
    Otherwise, replace localhost with the IP address of the host running wis2box. 

.. note::

    The MinIO package is required for running the script above.
    
    To install the MinIO package, run the following command:

    .. code-block:: bash

        pip3 install minio