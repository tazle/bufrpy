from __future__ import print_function

import bufrpy
from bufrpy.template import safnwc
from bufrpy.table import libbufr
import json
import sys
import time
import codecs

bufr_fname = None
if len(sys.argv) == 4:
    # b-table and d-table
    table = libbufr.read_tables(codecs.open(sys.argv[1], 'rb', 'utf-8'), codecs.open(sys.argv[2], 'rb', 'utf-8'))
    bufr_fname = sys.argv[3]
else:
    # either just b-table or a template file
    bufr_fname = sys.argv[2]
    try:
        # First try reading as safnwc template
        table = safnwc.read_template(codecs.open(sys.argv[1], 'rb', 'utf-8'))
    except Exception as e:
        # Try reading as libbufr table
        table = libbufr.read_tables(codecs.open(sys.argv[1], 'rb', 'utf-8'))
t_0 = time.time()

msg = bufrpy.bufrdec_file(open(bufr_fname, 'rb'), table)
t_1 = time.time()

out = json.dumps(bufrpy.to_json(msg))
t_2 = time.time()
dec = bufrpy.from_json(json.loads(out))
t_3 = time.time()

print(out)
