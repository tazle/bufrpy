def libbufr_compatible_rdt(msg):
    """
    Convert bufrpy output to a format that is equivalent to python-bufr output

    :param bufrpy.Message msg: BUFR message to convert
    :return: Output similar to that of python-bufr
    """
    def flatten(iterable, level=0):
        for el in iterable:
            if isinstance(el, list):
                
                if len(el) == 2:
                    pass
                elif level == 1 and len(el) == 54:
                    pass
                else:
                    if len(el) == 54:
                        print("54 at", level, file=sys.stderr)
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
            elif isinstance(x.value, unicode):
                yield "%d%03d.0" %(counter, len(x.value))
                counter += 1
            else:
                yield x.value
    return like_libbufr_values(msg.section4.data)
