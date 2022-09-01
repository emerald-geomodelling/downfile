import numpy

def coerce_numpy(downfile, data):
    if isinstance(data, numpy.bool_):
        return bool(data)
    elif isinstance(data, numpy.int64):
        return int(data)
    raise NotImplementedError("coerce_numpy registered for a type it does not support")
    
