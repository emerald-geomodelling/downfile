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
