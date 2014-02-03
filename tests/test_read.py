import unittest
import bufrpy
from .util import read_file

class TestReadBufr(unittest.TestCase):
    def test_sequence(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/tempLow_200707271955.bufr")

    def test_replication_sequence(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/1xBUFRSYNOP-ed4.bufr")

    def test_multiple_segments(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/3xBUFRSYNOP-com.bufr")

    def test_uncompressed_operators(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/207003.bufr")

    def test_compressed_operators(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/207003_compressed.bufr")
