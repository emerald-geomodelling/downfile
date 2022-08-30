# Downfile

Downfile can be used to serialize any data from Python in a controlled manner. The data is stored as a set of components in a ZIP file.
The format of each component is some standard format, such as JSON (for dictionaries etc) or Feather (for Pandas DataFrames).

To serialize or deserialize new types, methods can be registered using setuptools entry_points.

Example usage:

```
>>> data = {"bar": pd.DataFrame({"foo": [1, 2, 3]}), "fie": "hello"}
>>> downfile.dump(data, "test.down")

>>> data2 = downfile.parse("test.down")
>>> data2
{'bar':    foo
 0    1
 1    2
 2    3,
 'fie': 'hello'}
 ```

# How to add data formats

In setup.py in your own package add:

```
entry_points = {
    'downfile.dumpers': [
        'somepackage.somemodule.DataType=mypackage.mymodule:dumper',
    ],
    'downfile.parsers': [
        'myformat=mypackage.mymodule:parser',
    ]}
```

then in `mypackage.mymodule` provide the following two methods

```
def dumper(downfile, obj):
    name = downfile.new_file("myformat") # myformat is the filename extension
    with downfile.open_buffered(name, "w") as f:
        someFunctionToWriteObjToFile(f)
    return {"__jsonclass__": ["myformat", [name]]} # myformat is the key used to find `parser` in setp.py later

def parser(downfile, obj):    
    obj = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(obj, "r") as f:
        return someFunctionToReadObjFromFile(f)
```

`myformat` can be any string that is reasonably unique, typically the file extension used by the file format your're using for serialization.

If you're familiar with JSON RPC class hinting, you're probably wondering if dumper really has to write a file, or if it could just return some JSONifyable data. And the answer is nope, it doesn't need to write a file. If you're curious about serializing small objects, check out [the datetime handler](downfile/formats/format_datetime.py).
