from __future__ import print_function

import bufrpy
from bufrpy.template import safnwc
from bufrpy.table import libbufr
import json
import sys
import time
import codecs

try:
    # First try reading as safnwc template
    b_table = safnwc.read_template(codecs.open(sys.argv[1], 'rb', 'utf-8'))
except Exception as e:
    # Try reading as libbufr table
    b_table = libbufr.read_b_table(codecs.open(sys.argv[1], 'rb', 'utf-8'))
t_0 = time.time()

msg = bufrpy.bufrdec_file(open(sys.argv[2], 'rb'), b_table)
t_1 = time.time()

if msg.section3.n_subsets > 1:
    raise Exception("Can't deal with messages with more than 1 subset")

out = json.dumps(bufrpy.to_json(msg))
t_2 = time.time()
dec = bufrpy.from_json(json.loads(out))
t_3 = time.time()

print(out)
