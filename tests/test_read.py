import unittest
import codecs

import bufrpy
from bufrpy.table import libbufr

class TestReadBufr(unittest.TestCase):
    def test_sequence(self):
        msg = self._read("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/tempLow_200707271955.bufr")

    def test_replication_sequence(self):
        msg = self._read("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/1xBUFRSYNOP-ed4.bufr")

    def test_multiple_segments(self):
        msg = self._read("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/3xBUFRSYNOP-com.bufr")

    def _read(self, b_table_file, d_table_file, bufr_file):
        b_file = codecs.open(b_table_file, 'rb', 'utf-8')
        with b_file:
            d_file = codecs.open(d_table_file, 'rb', 'utf-8')
            with d_file:
                table = libbufr.read_tables(b_file, d_file)
                f = open(bufr_file, 'rb')
                with f:
                    return bufrpy.bufrdec_file(f, table)
