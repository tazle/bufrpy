import unittest
import bufrpy
from .util import read_file, read_file_debug, flatten_descriptors

class TestReadBufr(unittest.TestCase):
    def test_sequence(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/tempLow_200707271955.bufr")

    def test_replication_sequence(self):
        # Also BUFR edition 4 message
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/1xBUFRSYNOP-ed4.bufr")

    def test_multiple_segments(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/3xBUFRSYNOP-com.bufr")

    def test_uncompressed_operators(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/207003.bufr")

    def test_compressed_operators(self):
        # Has operators 1, 2 and 7
        msg1 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/207003.bufr")
        msg2 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/207003_compressed.bufr")

        _check_equal(msg1, msg2)

    def test_208035(self):
        # Has operator 8
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/208035.bufr")

    def test_associated(self):
        # Has operators 1, 2 and 4
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/associated.bufr")

    def test_change_refval(self):
        # Has operators 1 and 3
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/change_refval.bufr")

    def test_compressed_change_refval(self):
        # Has operators 1 and 3
        msg1 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/change_refval.bufr")
        msg2 = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/change_refval_compressed.bufr")

        _check_equal(msg1, msg2)

    def test_delayed_repetition(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/delayed_repetition.bufr")
        assert len(msg.section4.subsets[0].values) == 2
        assert len(msg.section4.subsets[0].values[0]) == 3
        for vs in msg.section4.subsets[0].values[0]:
            assert len(vs) == 2

    def test_compressed_delayed_repetition(self):
        msg = read_file("data/bt/B0000000000098013001.TXT", "data/bt/D0000000000098013001.TXT", "data/delayed_repetition_compressed.bufr")
        assert len(msg.section4.subsets) == 2
        for s in msg.section4.subsets:
            assert len(s.values) == 2
            assert len(s.values[0]) == 3
            for vs in s.values[0]:
                assert len(vs) == 2

def _check_equal(msg1, msg2):
    """
    Equality check that should match between compressed and uncompressed versions of a message.

    Skip section 0, because total length changes with compression
    Skip parts of section 3, because compression flag changes
    Skip parts of section 4, because its length changes with compression
    """
    assert msg1.section1 == msg2.section1
    assert msg1.section2 == msg2.section2
    assert msg1.section3.descriptors == msg2.section3.descriptors
    assert msg1.section4.subsets == msg2.section4.subsets
    assert msg1.section5 == msg2.section5
