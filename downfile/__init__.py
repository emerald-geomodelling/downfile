import json
import zipfile
import io
import os
import datetime
import pandas as pd
import contextlib
import shutil
import tempfile

class BufferedFile(zipfile.ZipFile):
    @contextlib.contextmanager
    def open_buffered(self, filename, mode="r", *arg, **kw):
        if mode == "w":
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmpname = tmp.name
                    yield tmp
                self.write(tmpname, filename)
            finally:
                os.unlink(tmpname)
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

    def serialize(self, data):
        # Make sure the root is always json so we get a 0.json
        return self.serialize_data({"root": data})
    
    def deserialize(self):
        return self.deserialize_data("0.json")["root"]

    def serialize_data(self, data):
        if isinstance(data, pd.DataFrame):
            return self.serialize_feather(data)
        elif isinstance(data, pd.Series):
            return self.serialize_feather(pd.DataFrame(data))
        else:
            return self.serialize_json(data)
        
    def serialize_feather(self, data):
        name = "%s.feather" % self.obj_idx
        self.obj_idx += 1
        with self.open_buffered(name, "w") as f:
            data.to_feather(f)
        return name
        
    def serialize_json(self, data):
        name = "%s.json" % self.obj_idx
        self.obj_idx += 1
        with self.open_buffered(name, "w") as f:
            with io.TextIOWrapper(f, "utf-8") as fu:
                json.dump(data, fu, default=self._serialise_json_default)
        return name

    def _serialise_json_default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"__jsonclass__":["datetime.datetime", [obj.strftime("%Y-%m-%d %H:%M:%S")]]}
        elif isinstance(obj, datetime.date):
            return {"__jsonclass__": ["datetime.date", [obj.strftime("%Y-%m-%d")]]}
        else:
            return {"__jsonclass__": ["file", [self.serialize_data(obj)]]}

    def deserialize_data(self, filename):
        ext = filename.rsplit(".", 1)[1]
        return getattr(self, "deserialize_" + ext)(filename)

    def deserialize_feather(self, filename):
        with self.open_buffered(filename, "r") as f:
            return pd.read_feather(f)
        
    def deserialize_json(self, filename):
        with self.open_buffered(filename, "r") as f:
            return json.load(io.TextIOWrapper(f, "utf-8"), object_hook=self._deserialize_json_object_hook)

    def _deserialize_json_object_hook(self, obj):
        if isinstance(obj,dict) and "__jsonclass__" in obj:
            cls = obj["__jsonclass__"][0]
            if cls == "datetime.datetime":
                obj = obj["__jsonclass__"][1][0]
                obj = datetime.datetime.strptime(obj, '%Y-%m-%d %H:%M:%S')
                return obj
            elif cls == "datetime.date":
                obj = obj["__jsonclass__"][1][0]
                obj = datetime.datetime.strptime(obj, '%Y-%m-%d').date()
                return obj
            elif cls == "file":
                return self.deserialize_data(obj["__jsonclass__"][1][0])
        return obj
