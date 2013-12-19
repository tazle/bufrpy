from bufrpy.util import slices, fxy2int, fxy
from bufrpy.descriptors import ElementDescriptor, ReplicationDescriptor, OperatorDescriptor

def read_b_table(line_stream):
    """
    Read BUFR B-table in from libbufr text file.

    :param line_stream: Iterable of lines, contents of the B-table file
    :return: Mapping from FXY integers to descriptors
    :rtype: dict
    :raises NotImplementedError: if the table contains sequence descriptors
    :raises ValueError: if the table contains descriptors with illegal class (outside range [0,3])
    """
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

