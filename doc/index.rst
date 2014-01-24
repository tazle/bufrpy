.. bufrpy documentation master file, created by
   sphinx-quickstart on Tue Dec 17 15:53:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

bufrpy
======

Bufrpy is a pure-Python BUFR message decoder. BUFR messages are
typically used to transmit meteorological observations. Bufrpy was
developed to work with NWCSAF_ RDT and HRW data, but there should not
be any reason why it could not be used with any BUFR messages, with
the following limitations:

* Messages with multiple data subsets are not supported
* Compressed messages are not supported
* Operator descriptors are not supported
* Sequence descriptors are not supported

Adding support for any of the above should be feasible, but we have
not encountered such data in our use of the library.

.. _NWCSAF: http://www.nwcsaf.org/

Examples
--------

Usage examples

.. toctree::
   :maxdepth: 2

   examples

Data Model
----------

Data model

.. toctree::
   :maxdepth: 2

   datamodel

API Documentation
-----------------

API documentation covers the public API

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

