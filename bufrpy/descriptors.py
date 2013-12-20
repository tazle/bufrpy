from collections import namedtuple

class ElementDescriptor(namedtuple('_ElementDescriptor', ['code', 'length', 'scale', 'ref', 'significance', 'unit'])):
    """Describes single value

    Data element described with an :class:`ElementDescriptor` is decoded into a
    :class:`.BufrValue`, with either textual or numeric value.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, in bits
    :ivar int scale: Scaling factor applied to value to get scaled value for encoding
    :ivar float ref: Reference value, subtracted from scaled value to get encoded value
    :ivar str significance: Semantics of the element
    :ivar str unit: Unit of the element, affects interpretation of the encoded data in case of e.g. textual vs. numeric values

    """
    __slots__ = ()

class ReplicationDescriptor(namedtuple('ReplicationDescriptor', ['code', 'length', 'fields', 'count', 'significance'])):
    """Describes a repeating collection of values
    
    Data described with a :class:`ReplicationDescriptor` is decoded
    into a list of lists of values. The outer list has one element per
    replication and the inner lists one element per replicated field.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, always 0
    :ivar int fields: Number of following descriptors to replicate
    :ivar int count: Number of replications
    :ivar str significance: Meaning of the replicated list
    """
    __slots__ = ()

class OperatorDescriptor(namedtuple('OperatorDescriptor', ['code', 'length', 'operation', 'operand', 'significance'])):
    """Significance unknown

    Not supported at the moment.
    """
    __slots__ = ()

class SequenceDescriptor(namedtuple('_SequenceDescriptor', ['code', 'length', 'descriptors', 'significance'])):
    """Describes a fixed sequence of elements in compact form

    Similar to a replication with count 1, but the encoded form is
    more compact, since the sequence of fields is implicit. Except
    that at least in NWCSAF Templates the constituent elements of the
    sequence are also present in the template.

    Not supported at the moment.

    """
    __slots__ = ()
