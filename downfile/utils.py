import importlib.metadata

def load_fn(name):
    mod, fn = name.rsplit(".", 1)
    return getattr(importlib.import_module(mod), fn)

def type_names(t):
    yield t.__module__ + "." + t.__name__
    for b in t.__bases__:
        for name in type_names(b):
            yield name
