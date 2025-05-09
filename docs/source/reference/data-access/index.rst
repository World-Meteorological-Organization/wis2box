.. _data-access:

Data access
===========

Overview
--------

This section provides examples of interacting with wis2box data services as described
in :ref:`services` using a number of common tools and software packages.

API
---

.. toctree::
   :maxdepth: 2

   python-api-requests
   python-api-owslib
   r-api
   qgis-api


Pub/Sub
-------

.. toctree::
   :maxdepth: 2

   python-mqp-subscribe


Running the examples
--------------------

To be able to run these examples, one needs to start up a Jupyter Notebook environment.  Below
is an example of starting a Jupyter session:

.. code-block:: bash

   git clone https://github.com/World-Meteorological-Organization/wis2box.git
   cd docs/source/data-access
   jupyter notebook --ip=0.0.0.0 --port=8888


When Jupyter starts up it may open a browser window for you. If not you would
need to to point a browser at http://localhost:8888 to see the menu of notebooks
available in this directory.


Summary
-------

The above examples provide a number of ways to utilize the wis2box suite of services.
