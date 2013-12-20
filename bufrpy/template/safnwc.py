from bufrpy.util import fxy2int, fxy
from bufrpy.descriptors import ElementDescriptor, ReplicationDescriptor, OperatorDescriptor
from bufrpy.template import Template

def read_template(line_stream):
    """
    Read SAFNWC message template into a :class:`.Template`

    SAFNWC template lines look as follows:

    ``1       001033  0       0        8             Code table        Identification of originating/generating centre``

    :param line_stream: Lines of SAFNWC template file
    :return: the template as Template
    :rtype: Template
    :raises ValueError: if the template contains a desccriptor outside range [0,3]
    """
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
    return Template(name, descriptors)
