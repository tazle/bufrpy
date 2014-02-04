import bufrpy
from bufrpy.table import libbufr
import codecs

def read_file(b_table_file, d_table_file, bufr_file):
    b_file = codecs.open(b_table_file, 'rb', 'utf-8')
    with b_file:
        d_file = codecs.open(d_table_file, 'rb', 'utf-8')
        with d_file:
            table = libbufr.read_tables(b_file, d_file)
            f = open(bufr_file, 'rb')
            with f:
                return bufrpy.bufrdec_file(f, table)

def read_file_debug(b_table_file, d_table_file, bufr_file):
    b_file = codecs.open(b_table_file, 'rb', 'utf-8')
    with b_file:
        d_file = codecs.open(d_table_file, 'rb', 'utf-8')
        with d_file:
            table = libbufr.read_tables(b_file, d_file)
            f = open(bufr_file, 'rb')
            with f:
                return bufrpy.bufrdec(bufrpy.util.ByteStream(f), table, skip_data=True)

def flatten_descriptors(descriptors):
    for d in descriptors:
        if isinstance(d, bufrpy.descriptors.SequenceDescriptor):
            for _d in d.descriptors:
                yield _d
        else:
            yield d
