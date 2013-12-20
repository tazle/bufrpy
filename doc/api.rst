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

BUFR Message
............

BUFR Message is represented as a :py:class:`.Message`.

.. autoclass:: bufrpy.Message


BUFR Template
.............

BUFR Template is represented as a :py:class:`.Template`.

.. autoclass:: bufrpy.template.Template

BUFR Descriptors
................

BUFR descriptors describe the data of the message. Atomic data
elements are described by :py:class:`.ElementDescriptor`, multiple
repetitions of a set of descriptors by
:py:class:`.ReplicationDescriptor`, fixed sequences of elements by
:py:class:`.SequenceDescriptor` and more complex structures by
:py:class:`.OperatorDescriptor`.

.. autoclass:: bufrpy.descriptors.ElementDescriptor
.. autoclass:: bufrpy.descriptors.ReplicationDescriptor
.. autoclass:: bufrpy.descriptors.OperatorDescriptor
.. autoclass:: bufrpy.descriptors.SequenceDescriptor

BUFR Values
...........

BUFR values are represented a instances of :py:class:`.BufrValue`.

.. autoclass:: bufrpy.value.BufrValue


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
