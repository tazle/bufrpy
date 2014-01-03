.. _api:

API
===

.. toctree::
   :maxdepth: 2

Reading BUFR messages
---------------------

.. autofunction:: bufrpy.bufrdec_file

.. autofunction:: bufrpy.bufrdec

.. autofunction:: bufrpy.bufrdec_all


BUFR message representation
---------------------------

BUFR Message
............

BUFR Message is represented as a :py:class:`.Message`.

.. autoclass:: bufrpy.Message

The :py:class:`.Message` contains several sections. Of these, sections
1, 3 and 4 are the most interesting. Section 1 contains message-level
metadata, section 3 describes message structure and section 4 contains
the actual data. Note that section 1 comes in multiple variants. The
variant used depends on which edition of the BUFR specification was
used to code the message.

.. autoclass:: bufrpy.Section1v3

.. autoclass:: bufrpy.Section1v4

.. autoclass:: bufrpy.Section3

.. autoclass:: bufrpy.Section4

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

BUFR values are represented a instances of :py:class:`.BufrValue`. The
values of one BUFR message subset are contained in a
:py:class:`.BufrSubset`.

.. autoclass:: bufrpy.value.BufrValue

.. autoclass:: bufrpy.value.BufrSubset


Reading BUFR tables
-------------------

.. autofunction:: bufrpy.table.libbufr.read_tables

Reading BUFR templates
----------------------

.. autofunction:: bufrpy.template.safnwc.read_template

JSON encoding/decoding
----------------------

.. autofunction:: bufrpy.to_json
.. autofunction:: bufrpy.from_json
