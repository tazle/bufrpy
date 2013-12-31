from collections import namedtuple
from abc import ABCMeta, abstractproperty

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

    def strong(self):
        return self

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

    def strong(self):
        return self

class OperatorDescriptor(namedtuple('OperatorDescriptor', ['code', 'length', 'operation', 'operand', 'significance'])):
    """Significance unknown

    Not supported at the moment.
    """
    __slots__ = ()

    def strong(self):
        return self

class SequenceDescriptor(object):
    """Describes a fixed sequence of elements in compact form

    Similar to a replication with count 1, but the encoded form is
    more compact, since the sequence of fields is implicit. Except
    that at least in NWCSAF Templates the constituent elements of the
    sequence are also present in the template.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, sum of lengths of constituent descriptors
    :ivar int descriptor_codes: Sequence containing constituent descriptor codes
    :ivar str significance: Meaning of the sequence, always empty string
    :ivar descriptors: Sequence containing constituent descriptors.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def code(self):
        pass

    @abstractproperty
    def length(self):
        pass

    @abstractproperty
    def descriptor_codes(self):
        pass

    @abstractproperty
    def significance(self):
        pass

    @abstractproperty
    def descriptors(self):
        pass

class StrongSequenceDescriptor(namedtuple('_SequenceDescriptor', ['code', 'length', 'descriptor_codes', 'significance', 'descriptors']), SequenceDescriptor):
    """
    SequenceDescriptor with direct references to child descriptors
    """
    __slots__ = ()

    def strong(self):
        return self

class LazySequenceDescriptor(namedtuple('_LazySequenceDescriptor', ['code', 'descriptor_codes', 'significance', 'descriptor_table']), SequenceDescriptor):
    """
    SequenceDescriptor with lazy references to child descriptors though the descriptor table
    """

    @property
    def length(self):
        return sum(x.length for x in self.descriptors)

    @property
    def descriptors(self):
        return tuple(self.descriptor_table[code] for code in self.descriptor_codes)

    def strong(self):
        return StrongSequenceDescriptor(self.code, self.length, self.descriptor_codes, self.significance, tuple(d.strong() for d in self.descriptors))
