from __future__ import print_function

from bufrpy.util import ByteStream, ReadableStream, int2fxy
from bufrpy.descriptors import ElementDescriptor, OperatorDescriptor, ReplicationDescriptor
from bufrpy.template import Template
from bufrpy.value import _decode_raw_value
import itertools
from collections import namedtuple, defaultdict
import re

class Section0(namedtuple("_Section0", ["length", "edition"])):
    """
    Represents Section 0 of a BUFR message.

    :ivar int length: Total message length, in bytes
    :ivar int edition: BUFR edition number
    """
    __slots__ = ()

class Section1(namedtuple("_Section1", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_subcategory", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute"])):
    """
    Section 1 of a BUFR edition 3 message.

    :ivar int length: Length of Section 1
    :ivar int master_table_id: Master table identifier
    :ivar int originating_centre: Originating/generating centre
    :ivar int originating_subcentre: Originating/generating subcentre
    :ivar int update_sequence_number: Update sequence number
    :ivar int optional_section: 0 if optional section not present, 1 if present
    :ivar int data_category: Data category (identifies Table A to be used)
    :ivar int data_subcategory: Data subcategory
    :ivar int master_table_version: Master table version
    :ivar int local_table_version: Local table version
    :ivar int year: Year (of century, add 1900 to get year AD, years post-1999 are coded as integers >= 100)
    :ivar int month: Month
    :ivar int day: Day
    :ivar int hour: Hour
    :ivar int minute: Minute
    """
    __slots__ = ()

class Section2(namedtuple("_Section2", ["length", "data"])):
    """
    Section 2 of a BUFR edition 3 message.

    :ivar int length: Length of Section 2
    :ivar data: Contents of section 2, as list of integers representing the content bytes
    """
    __slots__ = ()
Section3 = namedtuple("Section3", ["length", "n_subsets", "flags", "descriptors"])
Section4 = namedtuple("Section4", ["length", "data"])
Section5 = namedtuple("Section5", ["data"])

BufrMessage = namedtuple("BufrMessage", ["section0", "section1", "section2", "section3", "section4", "section5"])

def decode_section0(stream):
    """
    Decode Section 0 of a BUFR message into :class:`.Section0` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 0
    :rtype: Section0
    :raises ValueError: if the message does not start with BUFR
    """
    bufr = stream.readstr(4)
    if bufr != 'BUFR':
        raise ValueError("BUFR message must start with bytes BUFR, got: " + bufr)
    total_length = stream.readint(3)
    edition = stream.readint(1)
    return Section0(total_length, edition)

def decode_section1_v3(stream):
    """
    Decode Section 1 of version 3 BUFR message into :class:`.Section1` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 1
    :rtype: Section1
    :raises ValueError: if master table id is not 0
    """
    length = stream.readint(3)
    master_table_id = stream.readint(1)
    if master_table_id != 0:
        raise ValueError("Found master table value %d, only 0 supported" %master_table_id)
    originating_subcentre = stream.readint(1)
    originating_centre = stream.readint(1)
    update_sequence_number = stream.readint(1)
    optional_section = stream.readint(1)
    data_category = stream.readint(1)
    data_subcategory = stream.readint(1)
    master_table_version = stream.readint(1)
    local_table_version = stream.readint(1)
    year = stream.readint(1)
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    # Total bytes read this far is 17, read length-17 to complete the section
    rest = stream.readbytes(length-17)
    return Section1(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_subcategory, master_table_version, local_table_version, year, month, day, hour, minute)

def decode_section2_v3(stream):
    """
    Decode Section 2 of version 3 BUFR message into :class:`.Section2` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 2
    :rtype: Section2
    """
    length = stream.readint(3)
    data = list(stream.readbytes(length-3))
    return Section2(length, data)

def _decode_descriptors_table(length, stream, descriptor_table):
    # length is remaining length of descriptor field in bytes
    n_read = 0
    descriptors = []
    while n_read + 2 <= length:
        code = stream.readint(2)
        descriptors.append(descriptor_table[code])
        n_read += 2

    # read final byte, since length of the section should be even and
    # descriptors start at odd offset
    stream.readbytes(length-n_read)
    return descriptors

def _decode_descriptors_template(length, stream, descriptor_template):
    # length is remaining length of descriptor field in bytes
    n_read = 0
    codes = []
    while n_read + 2 <= length:
        code = stream.readint(2)
        codes.append(code)
        n_read += 2

    # read final byte, since length of the section should be even and
    # descriptors start at odd offset
    stream.readbytes(length-n_read)

    # check descriptor codes
    if len(codes) == len(descriptor_template.descriptors):
        for i, (code, descriptor) in enumerate(zip(codes, descriptor_template.descriptors)):
            if code != descriptor.code:
                raise ValueError("Invalid template, mismatch at index %d, template code: %d, message code: %d" %(i, descriptor.code, code))
        return descriptor_template.descriptors

    raise ValueError("Invalid template, length does not match message: template: %d, message: %d" %(len(descriptor_template.descriptors), len(codes)))

def decode_section3_v3(stream, descriptor_table):
    """
    :param ReadableStream stream: BUFR message, starting at section 3
    :param dict|Template descriptor_table: either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message

    If descriptor_table is a Template, it must match the structure of the message.
    """
    length = stream.readint(3)
    reserved = stream.readint(1)
    n_subsets = stream.readint(2)
    flags = stream.readint(1)
    # 7 bytes of headers so far

    if isinstance(descriptor_table, Template):
        descriptors = _decode_descriptors_template(length-7, stream, descriptor_table)
    else:
        descriptors = _decode_descriptors_table(length-7, stream, descriptor_table)
    return Section3(length, n_subsets, flags, descriptors)


def decode_section4_v3(stream, descriptors):
    from bitstring import ConstBitStream, Bits
    length = stream.readint(3)
    pad = stream.readint(1)
    data = stream.readbytes(length-4)
    bits = ConstBitStream(bytes=data)

    def decode(bits, descriptors):
        values = []
        for descriptor in descriptors:
            if isinstance(descriptor, ElementDescriptor):
                if descriptor.unit == 'CCITTIA5':
                    raw_value = Bits._readhex(bits, descriptor.length, bits.pos)
                else:
                    raw_value = Bits._readuint(bits, descriptor.length, bits.pos)
                bits.pos += descriptor.length
                values.append(_decode_raw_value(raw_value, descriptor))
            elif isinstance(descriptor, ReplicationDescriptor):
                aggregation = []
                if descriptor.count:
                    count = descriptor.count
                else:
                    count = decode(bits, itertools.islice(descriptors, 1))[0].value
                n_fields = descriptor.fields
                field_descriptors = list(itertools.islice(descriptors, n_fields))
                for _ in range(count):
                    aggregation.append(decode(bits, iter(field_descriptors)))
                values.append(aggregation)
            elif isinstance(descriptor, OperatorDescriptor):
                raise NotImplementedError("Don't know what to do with operators: %s" % descriptor)
            else:
                raise NotImplementedError("Unknown descriptor type: %s" % descriptor)
        return values

    values = decode(bits, iter(descriptors))
    return Section4(length, values)

def decode_section5_v3(stream):
    data = stream.readstr(4)
    END_TOKEN = "7777"
    if data != END_TOKEN:
        raise ValueError("Invalid end token: %s, expected: %s" %(data, END_TOKEN))
    return Section5(data)

def bufrdec_file(f, b_table):
    return bufrdec(ByteStream(f), b_table)

def bufrdec(stream, b_table):
    """ 
    See WMO306_vl2_BUFR3_Spec_en.pdf for BUFR format specification.

    :param ByteStream stream: stream that contains the bufr message
    :param dict|Template b_table: either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """

    rs = ReadableStream(stream)
    section0 = decode_section0(rs)
    if section0.edition != 3:
        raise ValueError("Encountered BUFR edition %d, only support 3" % section0.edition)
    section1 = decode_section1_v3(rs)
    if section1.optional_section != 0:
        section2 = decode_section2_v3(rs)
    else:
        section2 = None
    section3 = decode_section3_v3(rs, b_table)
    section4 = decode_section4_v3(rs, section3.descriptors)
    section5 = decode_section5_v3(rs)
    return BufrMessage(section0, section1, section2, section3, section4, section5)


    

if __name__ == '__main__':
    import sys
    b_table = read_libbufr_b_table(open(sys.argv[1], 'rb'))
    for fname in sys.argv[2:]:
        msg = bufrdec(ByteStream(open(fname, 'rb')), b_table)
    def printval(val, indentation=0):
        print(" "*indentation, int2fxy(val.descriptor.code), val.value, val.descriptor.significance)
    def printvals(vals, indentation=0):
        for val in vals:
            if isinstance(val, list):
                for mval in val:
                    printvals(mval, indentation+2)
                    print()
            else:
                printval(val, indentation)
    #printvals(msg.section4.data)
