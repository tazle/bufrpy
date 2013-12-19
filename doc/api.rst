.. _api:

API
===

.. toctree::
   :maxdepth: 2

Reading BUFR messages
---------------------

.. autofunction:: bufrpy.bufrdec

BUFR message representation
---------------------------

Reading BUFR tables
-------------------

.. autofunction:: bufrpy.table.libbufr.read_b_table

Reading BUFR templates
----------------------

.. autofunction:: bufrpy.template.safnwc.read_template

JSON encoding/decoding
----------------------

.. autofunction:: bufrpy.to_json
.. autofunction:: bufrpy.from_json
