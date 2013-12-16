import bufrdec
import json
import sys
import time

b_table = bufrdec.read_safnwc_template(open(sys.argv[1], 'rb'))
t_0 = time.time()

msg = bufrdec.bufrdec_file(open(sys.argv[2], 'rb'), b_table)
t_1 = time.time()
out = json.dumps(bufrdec.to_json(msg))
t_2 = time.time()
dec = bufrdec.from_json(json.loads(out))
t_3 = time.time()

print out
