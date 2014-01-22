bufrpy
======

Pure-Python BUFR decoding library

Supports Python 2 and Python 3.

Supports most common BUFR features, such as those used in NWCSAF RDT
and HRW data.

Quickstart
==========

First install the module.

    % pip install bufrpy

Then check that your BUFR files are readable using the module

    % python -m bufrpy.tool.bufr2json <templatefile> <bufrfile>

    --OR--

    % python -m bufrpy.tool.bufr2json <b-table-file> <bufrfile>

    --OR--

    % python -m bufrpy.tool.bufr2json <b-table-file> <d-table-file> <bufrfile>

Documentation
=============

See http://bufrpy.readthedocs.org/en/latest/

CI
==

See https://travis-ci.org/tazle/bufrpy
