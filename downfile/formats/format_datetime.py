import datetime

def datetime_to_json(downfile, obj):
    return {"__jsonclass__":["datetime.datetime", [obj.strftime("%Y-%m-%d %H:%M:%S")]]}
    
def date_to_json(downfile, obj):
    return {"__jsonclass__": ["datetime.date", [obj.strftime("%Y-%m-%d")]]}

def datetime_from_json(downfile, obj):
    obj = obj["__jsonclass__"][1][0]
    return datetime.datetime.strptime(obj, '%Y-%m-%d %H:%M:%S')

def date_from_json(downfile, obj):
    obj = obj["__jsonclass__"][1][0]
    return datetime.datetime.strptime(obj, '%Y-%m-%d').date()
