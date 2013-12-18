from bufrpy.descriptors import ElementDescriptor, ReplicationDescriptor, OperatorDescriptor, SequenceDescriptor
from bufrpy.value import _decode_raw_value
from bufrpy.bufrdec import BufrMessage, Section3, Section4

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
