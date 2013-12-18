from collections import namedtuple

ElementDescriptor = namedtuple('ElementDescriptor', ['code', 'length', 'scale', 'ref', 'significance', 'unit'])

ReplicationDescriptor = namedtuple('ReplicationDescriptor', ['code', 'length', 'fields', 'count', 'significance'])

OperatorDescriptor = namedtuple('OperatorDescriptor', ['code', 'length', 'operation', 'operand', 'significance'])

SequenceDescriptor = namedtuple('SequenceDescriptor', ['code', 'length', 'descriptors', 'significance'])
