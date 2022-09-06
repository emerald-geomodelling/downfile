import numpy

def coerce_numpy(downfile, data):
    if isinstance(data, numpy.bool_):
        return bool(data)
    elif isinstance(data, numpy.int64):
        return int(data)
    raise NotImplementedError("coerce_numpy registered for a type it does not support")
    
def to_npy(downfile, obj):
    name = downfile.new_file("npy")
    res = {"__jsonclass__": ["npy", [name]]}

    # Note: We use downfile for object dtypes, NOT pickle, so that
    # this is compatible between versions of Python and does not
    # introduce a security issue
    if obj.dtype != bool and obj.dtype != int and obj.dtype != float:
        obj = numpy.vectorize(lambda v: format_json.to_json_string(downfile, v))(obj)
    with downfile.open_buffered(name, "w") as f:
        numpy.save(f, obj, allow_pickle=False)
    return res

def from_npy(downfile, obj):
    name = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(name, "r") as f:
        res = numpy.load(file, mmap_mode=None, allow_pickle=False)

    if res.dtype != bool and res.dtype != int and res.dtype != float:
        res = numpy.vectorize(lambda v: fformat_json.from_json_string(downfile, v))(res)

    return res
