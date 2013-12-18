from collections import namedtuple
import codecs

BufrValue = namedtuple('BufrValue', ['raw_value', 'value', 'descriptor'])

def _decode_raw_value(raw_value, descriptor):
    if descriptor.unit == 'CCITTIA5': # Textual
        value = codecs.decode(raw_value.encode('iso-8859-1'),'hex_codec').decode('iso-8859-1') # CCITT IA5 is pretty close to ASCII, which is a subset of ISO-8859-1
    else: # Numeric
        if raw_value ^ ((1 << descriptor.length)-1) == 0: # Missing value, all-ones
            value = None
        else:
            value = 10**-descriptor.scale * (raw_value + descriptor.ref)
    return BufrValue(raw_value, value, descriptor)
