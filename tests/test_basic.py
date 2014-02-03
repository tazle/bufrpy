import unittest
import bufrpy
from .util import read_file

class TestSectionOps(unittest.TestCase):
    def test_equality(self):
        msg1 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/tempLow_200707271955.bufr")
        msg2 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/tempLow_200707271955.bufr")
        assert msg1 == msg2

