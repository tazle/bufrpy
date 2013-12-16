import bufrpy
import json
import sys
import time
import codecs

b_table = bufrpy.read_safnwc_template(codecs.open(sys.argv[1], 'rb', 'utf-8'))
t_0 = time.time()

msg = bufrpy.bufrdec_file(open(sys.argv[2], 'rb'), b_table)
t_1 = time.time()
out = json.dumps(bufrpy.to_json(msg))
t_2 = time.time()
dec = bufrpy.from_json(json.loads(out))
t_3 = time.time()

print out
