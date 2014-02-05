from __future__ import print_function

import bufrpy
from bufrpy.template import safnwc
from bufrpy.table import libbufr
from bufrpy.util import ByteStream
import json
import sys
import codecs

# Try reading as libbufr table
b_table = libbufr.read_b_table(codecs.open(sys.argv[1], 'rb', 'utf-8'))

stream = ByteStream(open(sys.argv[2], 'rb'))
messages, errors = bufrpy.decode_all(stream, b_table)
if errors:
    print(errors)
    sys.exit(1)
print(json.dumps(messages))
