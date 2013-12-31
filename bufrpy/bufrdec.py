from __future__ import print_function

from bufrpy.util import ByteStream, ReadableStream, int2fxy
from bufrpy.descriptors import ElementDescriptor, OperatorDescriptor, ReplicationDescriptor, SequenceDescriptor
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

class Section1v3(namedtuple("_Section1v3", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_subcategory", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute"])):
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
    :ivar int year: Year (originally of century, converted to AD by adding 1900)
    :ivar int month: Month
    :ivar int day: Day
    :ivar int hour: Hour
    :ivar int minute: Minute
    """
    __slots__ = ()

class Section1v4(namedtuple("_Section1v4", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_subcategory", "local_subcategory", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute", "second"])):
    """
    Section 1 of a BUFR edition 4 message.

    :ivar int length: Length of Section 1
    :ivar int master_table_id: Master table identifier
    :ivar int originating_centre: Originating/generating centre
    :ivar int originating_subcentre: Originating/generating subcentre
    :ivar int update_sequence_number: Update sequence number
    :ivar int optional_section: 0 if optional section not present, 1 if present
    :ivar int data_category: Data category (identifies Table A to be used)
    :ivar int data_subcategory: Data subcategory
    :ivar int local_subcategory: Local subcategory
    :ivar int master_table_version: Master table version
    :ivar int local_table_version: Local table version
    :ivar int year: Year (four digits)
    :ivar int month: Month
    :ivar int day: Day
    :ivar int hour: Hour
    :ivar int minute: Minute
    :ivar int second: Second
    """
    __slots__ = ()

class Section2(namedtuple("_Section2", ["length", "data"])):
    """
    Section 2 of a BUFR message.

    :ivar int length: Length of Section 2
    :ivar data: Contents of section 2, as list of integers representing the content bytes
    """
    __slots__ = ()

class Section3(namedtuple("_Section3", ["length", "n_subsets", "flags", "descriptors"])):
    """Section 3 of a BUFR message.

    Section 3 contains descriptors that describe the actual data
    format. Descriptors are instances of one of the descriptor
    classes: :py:class:`.descriptors.ElementDescriptor`,
    :py:class:`.descriptors.ReplicationDescriptor`,
    :py:class:`.descriptors.OperatorDescriptor`,
    :py:class:`.descriptors.SequenceDescriptor`.

    :ivar int length: Length of Section 3
    :ivar int n_subsets: Number of data subsets in the data section
    :ivar int flags: Flags describing the data set. See BUFR specification for details.
    :ivar descriptors: List of descriptors that describe the contents of each data subset.

    """
    __slots__ = ()

class Section4(namedtuple("_Section4", ["length", "data"])):
    """
    Section 4 of a BUFR message.

    Section 4 contains the actual message data.

    :ivar int length: Length of Section 4
    :ivar data: Message data as a list of BufrValues.
    """
    __slots__ = ()

class Section5(namedtuple("_Section5", ["data"])):
    """
    Section 5 of a BUFR message.

    :ivar data: End token.
    """
    __slots__ = ()


class Message(namedtuple("_Message", ["section0", "section1", "section2", "section3", "section4", "section5"])):
    """
    Represents a complete BUFR message, of either edition 3 or edition 4.

    :ivar Section0 section0: Section 0, start token and length
    :ivar Section1v3|Section1v4 section1: Section 1, time and source metadata
    :ivar Section2 section2: Section 2, optional metadata, not processed
    :ivar Section3 section3: Section 3, message structure
    :ivar Section4 section4: Section 4, message contents
    :ivar Section5 section5: Section 5, end token
    """
    __slots__ = ()

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
        raise ValueError("BUFR message must start with bytes BUFR, got: " + repr(bufr))
    total_length = stream.readint(3)
    edition = stream.readint(1)
    return Section0(total_length, edition)

def decode_section1_v3(stream):
    """
    Decode Section 1 of version 3 BUFR message into :class:`.Section1v3` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 1
    :rtype: Section1v3
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
    year = stream.readint(1) + 1900
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    # Total bytes read this far is 17, read length-17 to complete the section
    rest = stream.readbytes(length-17)
    return Section1v3(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_subcategory, master_table_version, local_table_version, year, month, day, hour, minute)

def decode_section1_v4(stream):
    """
    Decode Section 1 of version 4 BUFR message into :class:`.Section1v4` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 1
    :rtype: Section1v4
    :raises ValueError: if master table id is not 0
    """
    length = stream.readint(3)
    master_table_id = stream.readint(1)
    if master_table_id != 0:
        raise ValueError("Found master table value %d, only 0 supported" %master_table_id)
    originating_centre = stream.readint(2)
    originating_subcentre = stream.readint(2)
    update_sequence_number = stream.readint(1)
    optional_section = stream.readint(1)
    data_category = stream.readint(1)
    data_subcategory = stream.readint(1)
    local_subcategory = stream.readint(1)
    master_table_version = stream.readint(1)
    local_table_version = stream.readint(1)
    year = stream.readint(2)
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    second = stream.readint(1)
    # Total bytes read this far is 22, read length-22 to complete the section
    rest = stream.readbytes(length-22)
    return Section1v4(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_subcategory, local_subcategory, master_table_version, local_table_version, year, month, day, hour, minute, second)

def decode_section2(stream):
    """
    Decode Section 2 of a BUFR message into :class:`.Section2` object.

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

def decode_section3(stream, descriptor_table):
    """
    Decode Section 3, the descriptor section, of a BUFR message into a :class:`.Section3` object.

    If descriptor_table is a Template, it must match the structure of the message.

    :param ReadableStream stream: BUFR message, starting at section 3
    :param dict|Template descriptor_table: either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message
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


def decode_section4(stream, descriptors):
    """
    Decode Section 4, the data section, of a BUFR message into a :class:`.Section4` object.

    :param ReadableStream stream: BUFR message, starting at section 4
    :param descriptors: List of descriptors specifying message structure
    :raises NotImplementedError: if the message contains operator descriptors
    :raises NotImplementedError: if the message contains sequence descriptors
    """
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
            elif isinstance(descriptor, SequenceDescriptor):
                seq = decode(bits, descriptor.descriptors)
                values.extend(seq)
            else:
                raise NotImplementedError("Unknown descriptor type: %s" % descriptor)
        return values

    values = decode(bits, iter(descriptors))
    return Section4(length, values)

def decode_section5(stream):
    """
    Decode Section 5 of a BUFR message into a :class:`.Section5` object.

    Section 5 is just a trailer to allow verifying that the message has been read completely.

    :param ReadableStream stream: BUFR message, starting at section 5
    :raises ValueError: if message end token is not 7777 as specified
    """
    data = stream.readstr(4)
    END_TOKEN = "7777"
    if data != END_TOKEN:
        raise ValueError("Invalid end token: %s, expected: %s" %(data, END_TOKEN))
    return Section5(data)

def bufrdec_file(f, b_table):
    """
    Decode BUFR message from a file into a :class:`.Message` object.

    :param file f: File that contains the bufr message
    :param dict|Template b_table: Either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """
    return bufrdec(ByteStream(f), b_table)

READ_VERSIONS=(3,4)

def bufrdec_all(stream, b_table):
    """
    Decode all BUFR messages from stream into a list of :class:`.Message` objects and a list of decoding errors.
    

    Reads through the stream, decoding well-formed BUFR messages. BUFR
    messages must start with BUFR and end with 7777. Data between
    messages is skipped.

    :param ByteStream stream: Stream that contains the bufr message
    :param dict|Template b_table: Either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """
    def seek_past_bufr(stream):
        """ Seek stream until BUFR is encountered. Returns True if BUFR found and False if not """
        try:
            c = None
            while True:
                if c != b'B':
                    c = stream.next()
                    continue
                if c == b'B':
                    c = stream.next()
                    if c == b'U':
                        c = stream.next()
                        if c == b'F':
                            c = stream.next()
                            if c == b'R':
                                return True
                        
        except StopIteration:
            return False

    messages = []
    errors = []
    while seek_past_bufr(stream):
        try:
            msg = bufrdec(itertools.chain([b'B',b'U',b'F',b'R'], stream), b_table)
            messages.append(msg)
        except Exception as e:
            errors.append(e)
            pass
    return messages, errors

def bufrdec(stream, b_table):
    """ 
    Decode BUFR message from stream into a :class:`.Message` object.

    See WMO306_vl2_BUFR3_Spec_en.pdf for BUFR format specification.

    :param ByteStream stream: Stream that contains the bufr message
    :param dict|Template b_table: Either a dict containing mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """

    rs = ReadableStream(stream)
    section0 = decode_section0(rs)
    if section0.edition not in READ_VERSIONS:
        raise ValueError("Encountered BUFR edition %d, only support %s" %(section0.edition, READ_VERSIONS))
    if section0.edition == 3:
        section1 = decode_section1_v3(rs)
    elif section0.edition == 4:
        section1 = decode_section1_v4(rs)
    if section1.optional_section != 0:
        section2 = decode_section2(rs)
    else:
        section2 = None
    section3 = decode_section3(rs, b_table)
    section4 = decode_section4(rs, section3.descriptors)
    section5 = decode_section5(rs)
    return Message(section0, section1, section2, section3, section4, section5)


    

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
