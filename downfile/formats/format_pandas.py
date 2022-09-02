import pandas as pd
from . import format_json
import json

class CopyOnce(object):
    def __init__(self):
        self.copied = False
    def __call__(self, df):
        if self.copied:
            return df
        self.copied = True
        return df.copy()

def to_feather(downfile, obj):
    name = downfile.new_file("feather")
    res = {"__jsonclass__": ["feather", [name]]}

    copy_once = CopyOnce()
    
    # Feather files do not support fancy indices or columns, so store
    # them as separate feather files.
    if not type(obj.index) is pd.RangeIndex or not obj.index.equals(pd.RangeIndex.from_range(range(len(obj)))):
        res["index_name"] = obj.index.name
        res["index"] = pd.DataFrame(index=obj.index).reset_index()
        obj = copy_once(obj).reset_index(drop=True)
    elif obj.index.name is not None:
        res["index_name"] = obj.index.name
        obj = copy_once(obj)
        obj.index.name = None
    if obj.columns.inferred_type not in {"string", "unicode"}:
        res["columns_name"] = obj.columns.name
        res["columns"] = pd.DataFrame(index=obj.columns).reset_index()
        obj = copy_once(obj)
        obj.columns = [str(i) for i in range(len(obj.columns))]
    elif obj.columns.name is not None:
        res["columns_name"] = obj.columns.name
        obj = copy_once(obj)
        obj.columns.name = None

    # Handle columns with mixed value types
    obj_columns = [name for name, dtype in obj.dtypes.items() if dtype == "O"]
    if obj_columns:
        obj = copy_once(obj)
        for col in obj_columns:
            obj[col] = obj[col].apply(lambda v: format_json.to_json_string(downfile, v))
    
    with downfile.open_buffered(name, "w") as f:
        obj.to_feather(f)
    return res

def from_feather(downfile, obj):    
    name = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(name, "r") as f:
        res = pd.read_feather(f)
    if "index" in obj:
        res.index = obj["index"].set_index(list(obj["index"].columns)).index
    if "index_name" in obj:
        res.index.name = obj["index_name"]
    if "columns" in obj:
        res.columns = obj["columns"].set_index(list(obj["columns"].columns)).index
    if "columns_name" in obj:
        res.columns.name = obj["columns_name"]

    # Handle columns with mixed value types
    obj_columns = [name for name, dtype in res.dtypes.items() if dtype == "O"]
    for col in obj_columns:
        def decode_df_value(v):
            if not isinstance(v, str): return v
            try:
                return format_json.from_json_string(downfile, v)
            except json.JSONDecodeError:
                # Allow pure string columns for backwards compatibility...
                return v
        res[col] = res[col].apply(decode_df_value)
        
    return res
