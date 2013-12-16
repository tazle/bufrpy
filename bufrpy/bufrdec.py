import itertools
from bitstring import ConstBitStream, Bits
from collections import namedtuple, defaultdict
import re

# Decoder for RDT BUFR files

class ByteStream(object):
    def __init__(self, filelike):
        self.f = filelike

    def __iter__(self):
        return self

    def next(self):
        d = self.f.read(1)
        if len(d):
            return d
        else:
            raise StopIteration

class ReadableStream(object):
    def __init__(self, stream):
        self.stream = stream

    def readstr(self, n):
        """ Read n bytes as CCITT IA5 String """
        # TODO CCITT IA5 rather than ASCII
        return "".join(itertools.islice(self.stream, n))

    def readbytes(self, n):
        """ Read n bytes as bytes """
        return list(itertools.islice(self.stream, n))

    def readint(self, n):
        """ Read n-byte big-endian integer """
        bytes = list(itertools.islice(self.stream, n))
        return sum([ord(x) << 8*i for (i,x) in enumerate(reversed(bytes))])

class BufrTable(object):
    def __init__(self, descriptors):
        self.descriptors = descriptors

    def descriptor(self, descriptor_code):
        return self.descriptors[descriptor_code]

ElementDescriptor = namedtuple('ElementDescriptor', ['code', 'length', 'scale', 'ref', 'significance', 'unit'])

ReplicationDescriptor = namedtuple('ReplicationDescriptor', ['code', 'length', 'fields', 'count', 'significance'])

OperatorDescriptor = namedtuple('OperatorDescriptor', ['code', 'length', 'operation', 'operand', 'significance'])

SequenceDescriptor = namedtuple('SequenceDescriptor', ['code', 'length', 'descriptors', 'significance'])

BufrValue = namedtuple('BufrValue', ['raw_value', 'value', 'descriptor'])

Section0 = namedtuple("Section0", ["length", "edition"])
Section1 = namedtuple("Section1", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_sub_category", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute"])
Section2 = namedtuple("Section2", ["length", "data"])
Section3 = namedtuple("Section3", ["length", "n_subsets", "flags", "descriptors"])
Section4 = namedtuple("Section4", ["length", "data"])
Section5 = namedtuple("Section5", ["data"])

BufrMessage = namedtuple("BufrMessage", ["section0", "section1", "section2", "section3", "section4", "section5"])

BufrTemplate = namedtuple("BufrTemplate", ["name", "descriptors"])

def decode_section0(stream):
    bufr = stream.readstr(4)
    if bufr != 'BUFR':
        raise ValueError("BUFR message must start with bytes BUFR, got: " + bufr)
    total_length = stream.readint(3)
    edition = stream.readint(1)
    return Section0(total_length, edition)

def decode_section1_v3(stream):
    length = stream.readint(3)
    master_table_id = stream.readint(1)
    if master_table_id != 0:
        raise ValueError("Found master table value %d, only 0 supported" %master_table_id)
    originating_subcentre = stream.readint(1)
    originating_centre = stream.readint(1)
    update_sequence_number = stream.readint(1)
    optional_section = stream.readint(1)
    data_category = stream.readint(1)
    data_sub_category = stream.readint(1)
    master_table_version = stream.readint(1)
    local_table_version = stream.readint(1)
    year = stream.readint(1)
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    # Total bytes read this far is 17, read length-17 to complete the section
    rest = stream.readbytes(length-17)
    return Section1(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_sub_category, master_table_version, local_table_version, year, month, day, hour, minute)

def decode_section2_v3(stream):
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
    @param stream Byte stream containing the BUFR message
    @param descriptor_table either a dict containing mapping from BUFR descriptor codes to descriptors or a BufrTemplate describing the message

    If descriptor_table is a BufrTemplate, it must match the structure of the message.
    """
    length = stream.readint(3)
    reserved = stream.readint(1)
    n_subsets = stream.readint(2)
    flags = stream.readint(1)
    # 7 bytes of headers so far

    if isinstance(descriptor_table, BufrTemplate):
        descriptors = _decode_descriptors_template(length-7, stream, descriptor_table)
    else:
        descriptors = _decode_descriptors_table(length-7, stream, descriptor_table)
    return Section3(length, n_subsets, flags, descriptors)

def _decode_raw_value(raw_value, descriptor):
    if descriptor.unit == 'CCITTIA5': # Textual
        value = raw_value.decode('hex').decode('iso-8859-1') # CCITT IA5 is pretty close to ASCII, which is a subset of ISO-8859-1
    else: # Numeric
        if raw_value ^ ((1 << descriptor.length)-1) == 0: # Missing value, all-ones
            value = None
        else:
            value = 10**-descriptor.scale * (raw_value + descriptor.ref)
    return BufrValue(raw_value, value, descriptor)


def decode_section4_v3(stream, descriptors):
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
                for _ in xrange(count):
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

    @param stream ByteStream that contains the bufr message
    @param b_table either a dict containing mapping from BUFR descriptor codes to descriptors or a BufrTemplate describing the message
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

def slices(s, slicing):
    position = 0
    out = []
    for length in slicing:
        out.append(s[position:position + length])
        position += length
    return out

def fxy(fxy_code):
    # "fxxyyy" -> int(f),int(xx),int(yyy)
    # e.g. "001007" -> 0,1,7
    return map(int, slices(fxy_code, [1,2,3]))

def fxy2int(fxy_code):
    # "fxxyyy" -> int(f),int(xx),int(yyy) -> (f << 14 + xx << 8 + yyy)
    # e.g. "001007" -> 0,1,7 -> (0 << 14 + 1 << 6 + 7) = 263
    f,x,y = fxy(fxy_code)
    return (f << 14) + (x << 8) + y

def int2fxy(code):
    # Inverse of fxy2int
    f = code >> 14 & 0x3
    x = code >> 8 & 0x3f
    y = code & 0xff
    return "%d%02d%03d" %(f,x,y)

def read_libbufr_b_table(line_stream):
    descriptors = {}
    for line in line_stream:
        # Format from btable.F:146 in libbufr version 000400
        parts = slices(line, [1,6,1,64,1,24,1,3,1,12,1,3])
        raw_descriptor = parts[1]
        descriptor_code = fxy2int(raw_descriptor)
        significance = parts[3].strip()
        unit = parts[5].strip()
        scale = int(parts[7])
        reference = int(parts[9])
        bits = int(parts[11])

        descr_class = raw_descriptor[0]
        if descr_class == '0':
            descriptors[descriptor_code] = ElementDescriptor(descriptor_code, bits, scale, reference, significance, unit)
        elif descr_class == '1':
            f,x,y = fxy(raw_descriptor)
            descriptors[descriptor_code] = ReplicationDescriptor(descriptor_code, 0, x, y, significance)
        elif descr_class == '2':
            f,x,y = fxy(raw_descriptor)
            descriptors[descriptor_code] = OperatorDescriptor(descriptor_code, 0, x, y, significance)
        elif descr_class == '3':
            raise NotImplementedError("Support for sequence descriptors not implemented yet")
        else:
            raise ValueError("Encountered unknown descriptor class: %s" %descr_class)
    return descriptors

def read_safnwc_template(line_stream):
    descriptors = []
    metadata = {}
    for l in line_stream:
        if l.startswith("#") or l.startswith("/*"):
            # Ignore comments, does not support multiline comments properly
            continue
        elif l.startswith("NUM"):
            name, num = l.split(" ")
            metadata[name] = int(num)
        else:
            # Input lines look like this:
            # 1       001033  0       0        8             Code table        Identification of originating/generating centre
            num = int(l[:8])
            raw_descriptor = l[8:14]
            descriptor_code = fxy2int(raw_descriptor)
            scale = int(l[14:23])
            reference = int(l[23:33])
            bits = int(l[33:47])
            unit = l[47:65].strip()[:24]
            significance = l[65:].strip()[:64]

            descr_class = raw_descriptor[0]
            if descr_class == '0':
                descriptors.append(ElementDescriptor(descriptor_code, bits, scale, reference, significance, unit))
            elif descr_class == '1':
                f,x,y = fxy(raw_descriptor)
                descriptors.append(ReplicationDescriptor(descriptor_code, 0, x, y, significance))
            elif descr_class == '2':
                f,x,y = fxy(raw_descriptor)
                descriptors.append(OperatorDescriptor(descriptor_code, 0, x, y, significance))
            elif descr_class == '3':
                # Ignore sequence descriptors, they are followed by constituent elements in the SAFNWC template format
                continue
            else:
                raise ValueError("Encountered unknown descriptor class: %s" %descr_class)
    name = "B0000000000%(NUM_ORIGINATING_CENTRE)03d%(NUM_BUFR_MAIN_TABLE)03d%(NUM_BUFR_LOCAL_TABLES)03d.TXT" %metadata
    return BufrTemplate(name, descriptors)
        

def libbufr_compatible_rdt(data):
    def flatten(iterable, level=0):
        for el in iterable:
            if isinstance(el, list):
                
                if len(el) == 2:
                    pass
                elif level == 1 and len(el) == 54:
                    pass
                else:
                    if len(el) == 54:
                        print >> sys.stderr, "54 at", level
                    yield BufrValue(len(el), len(el), None)
                for x in flatten(el,level+1):
                    yield x
            else:
                yield el

    def like_libbufr_values(data):
        counter = 1
        for x in flatten(data):
            if x.value is None:
                yield 1.7e38
            elif isinstance(x.value, int):
                yield str(x.value) + ".0"
            elif isinstance(x.value, float):
                if int(x.value) == x.value:
                    yield str(int(x.value)) + ".0"
                else:
                    yield x.value
                    #yield re.sub("\.$", ".0", ("%20.5f" %x.value).rstrip("0")).strip(" ")
            elif isinstance(x.value, unicode):
                yield "%d%03d.0" %(counter, len(x.value))
                counter += 1
            else:
                yield x.value
    return like_libbufr_values(msg.section4.data)

def to_json(msg):
    descriptor_index = {}
    for i,descriptor in enumerate(msg.section3.descriptors):
        descriptor_index[descriptor] = i

    def to_json_data(data):
        result = []
        for el in data:
            if isinstance(el, list):
                result.append(to_json_data(el))
            else:
                result.append({"desc":descriptor_index[el.descriptor], "val":el.raw_value})
        return result

    result = {"descriptors":msg.section3.descriptors, "data":to_json_data(msg.section4.data)}
    return result

def from_json(json_obj):
    descriptor_types = {0:ElementDescriptor, 1:ReplicationDescriptor, 2:OperatorDescriptor, 3:SequenceDescriptor}
    descriptors = []
    for descriptor_def in json_obj["descriptors"]:
        dtype = descriptor_def[0] >> 14 & 0x3
        klass = descriptor_types[dtype]
        descriptors.append(klass(*descriptor_def))

    def decode_data(json_data):
        result = []
        for el in json_data:
            if isinstance(el, dict):
                descriptor = descriptors[el["desc"]]
                result.append(_decode_raw_value(el["val"], descriptor))
            else:
                result.append(decode_data(el))
        return result

    data = decode_data(json_obj["data"])
            
    return BufrMessage(None, None, None, Section3(None, None, None, descriptors), Section4(None, data), None)
    

if __name__ == '__main__':
    import sys
    b_table = read_libbufr_b_table(open(sys.argv[1], 'rb'))
    for fname in sys.argv[2:]:
        msg = bufrdec(ByteStream(open(fname, 'rb')), b_table)
    def printval(val, indentation=0):
        print " "*indentation, int2fxy(val.descriptor.code), val.value, val.descriptor.significance
    def printvals(vals, indentation=0):
        for val in vals:
            if isinstance(val, list):
                for mval in val:
                    printvals(mval, indentation+2)
                    print
            else:
                printval(val, indentation)
    #printvals(msg.section4.data)
