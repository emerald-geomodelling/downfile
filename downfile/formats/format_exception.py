from .. import utils
import builtins

def is_exc(val):
    return isinstance(val, type) and issubclass(val, Exception)
builtin_exceptions = set(["builtins." + name for name in dir(builtins)
                          if is_exc(getattr(builtins, name))])
 
def exception_to_json(downfile, obj):
    return {"__jsonclass__":["exception"],
            "args": obj.args,
            "type": list(utils.type_names(type(obj)))}

def exception_from_json(downfile, obj):
    basetype = [name for name in obj["type"] if name in builtin_exceptions][0]
    return getattr(builtins, basetype[len("builtins."):])(*obj["args"])
