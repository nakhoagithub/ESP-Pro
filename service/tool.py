import ujson
import os

config_path = "conf.json"
module_path = "modules.json"
sensor_path = "sensors.json"

def file_or_dir_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def init_default():
    try:
        if not file_or_dir_exists(config_path):
            with open(config_path, "w") as file:
                ujson.dump({}, file)
            print(f"File {config_path} created.")
            
        if not file_or_dir_exists(module_path):
            with open(module_path, "w") as file:
                ujson.dump({}, file)
            print(f"File {module_path} created.")
            
        if not file_or_dir_exists(sensor_path):
            with open(sensor_path, "w") as file:
                ujson.dump({}, file)
            print(f"File {sensor_path} created.")
            
    except OSError as e:
        print(f"Can not create config file: {e}")


def conf():
    try:
        with open(config_path, "r") as file:
            data = ujson.load(file)
            return data
    except OSError as e:
        print(f"Can not open file: {str(e)}")
        return None
    except ValueError as e:
        print(f"Can not read JSON from {config_path}")
        return None
    

def save_conf(key, value) -> dict:
    data = {}
    try:
        with open(config_path, "r") as file:
            data = ujson.load(file)

        data[key] = value
        
        if value is None and key in data:
            del data[key]
            
        with open(config_path, "w") as file:
            ujson.dump(data, file)
        
        print("Update Success!")
    except OSError as e:
        print(f"Can not open file: {str(e)}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    return data


def modules():
    try:
        with open(module_path, "r") as file:
            data = ujson.load(file)
            return data
    except OSError as e:
        print(f"Can not open file: {str(e)}")
        return None
    except ValueError as e:
        print(f"Can not read JSON from {module_path}")
        return None


def save_module(address: int, start: int = None, count: int = None, func: int = None, on: int = None, off: int = None, delete=False):
    data = {}
    try:
        with open(module_path, "r") as file:
            data = ujson.load(file)
        
        if address is not None and str(address) in data and delete:
            del data[f"{address}"]
        else:
            if address is not None and start is not None and count is not None and func is not None and on is not None and off is not None:
                data[f"{address}"] = {
                    "address": address,
                    "func": func,
                    "on": on,
                    "off": off,
                    "start": start,
                    "count": count,
                }
            
        with open(module_path, "w") as file:
            ujson.dump(data, file)
            
    except OSError as e:
        print(f"Can not open file: {str(e)}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    return data


def sensors():
    try:
        with open(sensor_path, "r") as file:
            data = ujson.load(file)
            return data
    except OSError as e:
        print(f"Can not open file: {str(e)}")
        return None
    except ValueError as e:
        print(f"Can not read JSON from {sensor_path}")
        return None


def save_sensor(address: int, start: int = None, count: int = None, func: int = None, delete=False):
    data = {}
    try:
        with open(sensor_path, "r") as file:
            data = ujson.load(file)
        
        if address is not None and str(address) in data and delete:
            del data[f"{address}"]
        else:
            if address is not None and start is not None and count is not None and func is not None:
                data[f"{address}"] = {
                    "address": address,
                    "func": func,
                    "start": start,
                    "count": count,
                }
            
        with open(sensor_path, "w") as file:
            ujson.dump(data, file)
            
    except OSError as e:
        print(f"Can not open file: {str(e)}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    return data


def find_where(data: list, **conditions):
    results = []
    for item in data:
        match = True
        for key, value in conditions.items():
            if key not in item or item[key] != value:
                match = False
                break
        if match:
            results.append(item)
    return results  
        
        
