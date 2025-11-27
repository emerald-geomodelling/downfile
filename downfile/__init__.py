import zipfile
import os
import datetime
import pandas as pd
import contextlib
import shutil
import tempfile
import importlib.metadata
from .utils import *

#parsers = {entry.name: entry.load() for entry in importlib.metadata.entry_points()['downfile.parsers']}
#dumpers = {entry.name: entry.load() for entry in importlib.metadata.entry_points()['downfile.dumpers']}

from importlib.metadata import entry_points

eps = entry_points()
parsers = {entry.name: entry.load() for entry in importlib.metadata.entry_points(group='downfile.parsers')}
dumpers = {entry.name: entry.load() for entry in importlib.metadata.entry_points(group='downfile.dumpers')}

class BufferedFile(zipfile.ZipFile):
    @contextlib.contextmanager
    def open_buffered(self, filename, mode="r", *arg, **kw):
        if mode == "w":
            tmpname = None
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmpname = tmp.name
                    yield tmp
                self.write(tmpname, filename)
            finally:
                if tmpname: os.unlink(tmpname)
        elif mode == "r":
            tempdir = tempfile.mkdtemp()
            try:
                extractedpath = self.extract(filename, path=tempdir)
                with open(extractedpath, "rb") as f:
                    yield f
            finally:
                shutil.rmtree(tempdir)
        else:
            raise ValueError("Unknown mode " + mode)

class DownFile(BufferedFile):
    def __init__(self, *arg, **kw):
        zipfile.ZipFile.__init__(self, *arg, **kw)
        self.obj_idx = 0

    def new_file(self, ext):
        name = "%s.%s" % (self.obj_idx, ext)
        self.obj_idx += 1
        return name
        
    def serialize(self, data):
        # Make sure the root is always json so we get a 0.json
        return self.serialize_data({"root": data})
    
    def serialize_data(self, data):
        for typename in type_names(type(data)):
            if typename in dumpers:
                return dumpers[typename](self, data)
        assert False, "Unknown datatype " + type(data).__module__ + "." + type(data).__name__
            
    def deserialize(self):
        return self.deserialize_data({"__jsonclass__": ["json", ["0.json"]]})["root"]

    def deserialize_data(self, obj):
        if "__jsonclass__" in obj:
            return parsers[obj["__jsonclass__"][0]](self, obj)
        return obj

def parse(path):
    with DownFile(path, "r") as f:
        return f.deserialize()

def dump(obj, path):
    with DownFile(path, "w") as f:
        f.serialize(obj)
