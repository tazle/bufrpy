from itertools import islice

class ByteStream(object):
    """
    Stream of bytes, represented as length-1 (byte) strings
    """
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

    __next__ = next

class ReadableStream(object):
    """Wrapper for ByteStream with additional operations for reading
    structures such as strings and variable-width integers.
    """
    def __init__(self, stream):
        self.stream = stream

    def readstr(self, n):
        """ Read n bytes as CCITT IA5 String """
        # TODO CCITT IA5 rather than ISO-8859-1
        return b"".join(islice(self.stream, n)).decode('iso-8859-1')

    def readbytes(self, n):
        """ Read n bytes as list of ints """
        return list(ord(x) for x in islice(self.stream, n))

    def readint(self, n):
        """ Read n-byte big-endian integer """
        bytes = list(islice(self.stream, n))
        return sum([ord(x) << 8*i for (i,x) in enumerate(reversed(bytes))])
