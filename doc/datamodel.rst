.. _examples:

Data Model
==========

Bufrpy data model matches that of the BUFR messages fairly closely,
though not as closely as libbufr or the Python libbufr
wrappers. Typically BUFR messages are stored in a file so that the
file contains a single BUFR message. Some applications (e.g. SAFNWC
HWR) store multiple messages in a single file, requiring some tricks
to read them.

The top-level data structure in :py:mod:`bufrpy` is
:py:class:`.Message` that corresponds to one BUFR message. A BUFR
message contains 6 sections, some of which contain metadata and some
the actual data. The most important sections are numbers 3 and 4.
They contain data descriptors and the data itself
respectively. Logically BUFR files contain at least one *subset* of
data. Each subset follows the same structure, defined by the data
descriptors in section 3. In :py:mod:`bufrpy`, sections are attributes
of :py:class:`.Message`. Section 4 contains the data subsets as a list
of :py:class:`.BufrSubset` objects. 

Logically each subset is a linear sequence of data values. All
metadata about the data is stored in the descriptors. However, there
are certain looping constructs (replication descriptors) that allow
repetition of a sequence of data items. This leads to hierarchical
logical structure. Physically the data is still stored in a linear
sequence (or in interleaved fashion if a message has multiple data
subsets). In :py:mod:`bufrpy` the data of each dataset is represented
by a list of :py:class:`.BufrValue` objects. A replicated sequence in
the data is represented by a list of lists of :py:class:`.BufrValue`
objects so that the outer list contains one list for each repetition,
and the inner lists are equivalent to :py:attr:`~.BufrSubset.values`
of a :py:class:`.BufrSubset`. Hierarchical data is thus naturally
represented as nested lists.

