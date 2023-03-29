# Downfile

Downfile can be used to serialize any data from Python in a controlled manner. The data is stored as a set of components in a ZIP file.
The format of each component is some standard format, such as JSON (for dictionaries etc) or Feather (for Pandas DataFrames).

To serialize or deserialize new types, methods can be registered using setuptools entry_points.

Since a (de)serializer has to be written manually for each type, it does not have the same security and compatibility issues that Pickle has, but instead comes with a slightly higher development overhead.

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
# Builtin support for datatypes

* Python base types: int, float, bool, str, dict, list
* Python builtin exceptions
* Pandas DataFrames
* Numpy arrays

# How to add data types / formats

In `setup.py` in your own package (say `mypippackage`) add:

```
entry_points = {
    'downfile.dumpers': [
        'somepackage.somemodule.DataType=mypippackage.mymodule:dumper',
    ],
    'downfile.parsers': [
        'mypippackage.myformat=mypackage.mymodule:parser',
    ]}
```

then in `mypackage.mymodule` provide the following two methods

```
def dumper(downfile, obj):
    # Here `mypippackage.myformat` is the filename extension.
    # If the file format has a standard extension, such as `.png`, `.csv` etc,
    # you might want to use that here instead.
    name = downfile.new_file("mypippackage.myformat")
    with downfile.open_buffered(name, "w") as f:
        someFunctionToWriteObjToFile(f)
    # Here mypippackage.myformat is the key used to find `parser` in `setp.py` later.
    return {"__jsonclass__": ["mypippackage.myformat", [name]]}

def parser(downfile, obj):    
    name = obj["__jsonclass__"][1][0]
    with downfile.open_buffered(name, "r") as f:
        return someFunctionToReadObjFromFile(f)
```

`mypippackage.myformat` can be any string that is reasonably unique, typically the file extension used by the file format your're using for serialization. However, it is good practice to include the pip package name for your package, so that people can easily find out what packages are missing when failing to parse a file!

If you're familiar with JSON RPC class hinting, you're probably wondering if dumper really has to write a file, or if it could just return some JSONifyable data. And the answer is nope, it doesn't need to write a file. If you're curious about serializing small objects, check out [the datetime handler](downfile/formats/format_datetime.py).

To recursively encode some component value of the data you're encoding, you can use `downfile.formats.format_json.to_json_string(downfile, v)`. This will encode the value v to JSON, using the same class hinting structure used in the main JSON file, that is, allowing any complex type to be serialized as external files, and return the encoded JSON value.

## Downfile instances
The `downfile` argument to `dumper`/`parser` above is an instance of `downfile.Downfile`, which is a subclass of `zipfile.ZipFile` that implements a few extra methods: `new_file(extension)` returns a new unique filename, `open_buffered(filename, mode="r"|"w")` works like `open()`, but uses a temporary file so that multiple files can be opened concurrently (`zipfile.ZipFile.open()` does not support this).

# Data format details

* A Downfile is a zip file
* A Downfile must contain a JSON file named `0.json`
  * This JSON file must contain an object with a key `root`
  * The content of the `root` key is considered the content of the entire Downfile.
* Any file inside a Downfile can reference additional files inside the Downfile using relative paths
* Any JSON file inside a Downfile can use [JSON RPC 1.0 class hinting](https://www.jsonrpc.org/specification_v1#a3.JSONClasshinting)
* A class hint of `{"__jsonclass__": ["mypippackage.myformat", ["filename.ext"]]}` must be used for data that is stored in a separate file inside the Downfile

## Storage of datetimes and dates

* Uses the class hints `{"__jsonclass__":["datetime.datetime", ["%Y-%m-%d %H:%M:%S"]]}` and `{"__jsonclass__": ["datetime.date", ["%Y-%m-%d"]]}`
* Does not store any external file

## Storage of exceptions

* Uses the class hint `{"__jsonclass__":["exception"]}`
* `args` property of the class hint object holds exception arguments
* `type` property of the class hint object holds a list of string names for all classes in the inheritance list of the exception, most specific first. The names are prefixed with their respective module name.
* Does not store any external file

## Storage of Pandas DataFrames

* Uses the class hint `{"__jsonclass__": ["feather", [name]]}`
* Stored as a feather file
* Any object column will have its cell values encoded as JSON with the same class hinting used for the main JSON file.
* To allow for more complex columans and indices (e.g. multilevel, numeric columns etc) not supported by the feather format, columns and index can optionally be converted to dataframes and stored separately (using the same method)
  * The index is stored in a property `index` on the class hint object, and its name in a property `index_name`
  * The columns are stored in a property `columns` on the class hint object, and its name in a property `columns_name`
 
 ## Storage of Numpy arrays
 * Uses the class hint `{"__jsonclass__": ["npy", [name]]}`
 * Stored as an `.npy`
 * If dtype is `Object`, values are encoded as JSON with the same class hinting used for the main JSON file, meaning that the pickle based encoder of Numpy is never triggered.
 
