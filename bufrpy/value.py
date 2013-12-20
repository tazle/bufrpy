from collections import namedtuple
import codecs

class BufrValue(namedtuple('BufrValue', ['raw_value', 'value', 'descriptor'])):
    """Contains single value

    Contains single value, both in raw and decoded form, plus a link
    to its descriptor.

    :ivar str|int raw_value: Raw value. Either as hex-encoded string for textual values or an unsigned integer for numeric values
    :ivar str|int|float|None value: Decoded value. Value decoded according to its descriptor. Textual values are strings and numeric values floats or ints. Missing value is indicated by :py:data:`None`.
    :ivar ElementDescriptor descriptor: The descriptor of this value
    """
    __slots__ = ()

def _decode_raw_value(raw_value, descriptor):
    if descriptor.unit == 'CCITTIA5': # Textual
        value = codecs.decode(raw_value.encode('iso-8859-1'),'hex_codec').decode('iso-8859-1') # CCITT IA5 is pretty close to ASCII, which is a subset of ISO-8859-1
    else: # Numeric
        if raw_value ^ ((1 << descriptor.length)-1) == 0: # Missing value, all-ones
            value = None
        else:
            value = 10**-descriptor.scale * (raw_value + descriptor.ref)
    return BufrValue(raw_value, value, descriptor)
