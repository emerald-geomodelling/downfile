import pandas as pd

def to_feather(downfile, obj):
    name = downfile.new_file("feather")
    with downfile.open_buffered(name, "w") as f:
        obj.to_feather(f)
    return {"__jsonclass__": ["feather", [name]]}

def from_feather(downfile, obj):    
    obj = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(obj, "r") as f:
        return pd.read_feather(f)
