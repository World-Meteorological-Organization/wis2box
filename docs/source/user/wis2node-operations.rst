.. _wis2node-operations:

Operating a WIS2 Node
=====================

This section provides information on how to register and maintain a WIS2 Node using wis2box.

WIS2 Node registration
-----------------------

For a wis2box instance to start sharing data with the global WIS2 network, it must be registered as a WIS2 Node.

Following registration, WIS2 Global Brokers will subscribe to the WIS2 Node and republish all valid WIS2 data notifications published under ``origin/a/wis2/CENTRE_ID/#`` topic, where
``CENTRE_ID`` is the unique identifier for the WIS2 Node, as defined by the datasets configured in wis2box.

Registration of a WIS2 Node must be approved by the Permanent Representative with WMO (PR) for the country or territory in which the WIS Centre resides.

The National Focal Point (NFP) on WIS matters can register a WIS2 Node on behalf of the PR for an official NC or DCPC listed in the Manual on WMO Information System 
(WMO-No. 1060), Volume I - Appendix B: Approved WIS Centres.

For more information see the section `WIS2 Node Registration`_ on the WMO community website.

WIS2 Node maintenance
---------------------

The Data Publisher is responsible for maintaining the WIS2 Node, keeping the associated datasets up to date, and ensuring the data is valid and compliant with WIS2 standards
and any other WMO regulations specific to the data types being published.

It is recommended to regularly check the Grafana dashboards inside wis2box to verify that data is being published and monitor for any errors.

Maintaining discovery metadata
------------------------------

To verify that your metadata records have been published, search for the wis2box centre-id in any of the WIS2 Global Discovery Catalogues:

For example to see the records for centre-id `br-inmet`, query the WIS2 Global Discovery Catalogues as follows:

- **GDC ECCC**: https://wis2-gdc.weather.gc.ca/collections/wis2-discovery-metadata/items?q=br-inmet
- **GDC DWD**: https://wis2.dwd.de/gdc/collections/wis2-discovery-metadata/items?q=br-inmet
- **GDC CMA**: https://gdc.wis.cma.cn/collections/wis2-discovery-metadata/items?q=br-inmet

If any datasets are missing, login to wis2box-management container and republish the missing datasets using the following command:

.. code-block:: bash

   python3 wis2box-ctl.py login
   wis2box metadata discovery republish

Ensure to use wis2box version 1.1.0 or later to ensure the metadata is validated before republishing.

If the WIS2 Global Discovery Catalogue contains outdated metadata records, use the following command to send a notification to delete the record:

.. code-block:: bash

   python3 wis2box-ctl.py login
   wis2box metadata discovery unpublish urn:wmo:md:my-centre-id:my-local-id

Ensure to replace `urn:wmo:md:my-centre-id:my-local-id` with the actual identifier of the metadata record as recorded in the WIS2 Global Discovery Catalogue.

.. _`WIS2 Node Registration`: https://community.wmo.int/en/activity-areas/wis/WIS2-overview#WIS2_Node_Registration
