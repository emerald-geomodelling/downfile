import io
import json

def to_json(downfile, data):
    name = downfile.new_file("json")
    with downfile.open_buffered(name, "w") as f:
        with io.TextIOWrapper(f, "utf-8") as fu:
            json.dump(data, fu, default=downfile.serialize_data)
    return {"__jsonclass__": ["json", [name]]}

def from_json(downfile, obj):
    obj = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(obj, "r") as f:
        try:
            return json.load(io.TextIOWrapper(f, "utf-8"), object_hook=downfile.deserialize_data)
        except Exception as e:
            raise ValueError("Unable to parse JSON from " + obj) from e

# These are NOT dumpers/loaders, but might be usefull in implementing other dumpers/loaders
def to_json_string(downfile, data):
    return json.dumps(data, default=downfile.serialize_data)

def from_json_string(downfile, json_string):
    try:
        return json.loads(json_string, object_hook=downfile.deserialize_data)
    except Exception as e:
        raise ValueError("Unable to parse JSON: <" + json_string + ">") from e
