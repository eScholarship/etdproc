import importlib.util
import inspect
import os
import consts

def load_module_from_file(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract_class_constants(module):
    result = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Only include classes defined in this module
        if obj.__module__ == module.__name__:
            for key, value in vars(obj).items():
                if not key.startswith('__') and not callable(value):
                    result[f"{name}.{key}"] = value
    return result

def save_in_db(data):
    for key in data:
        consts.db.addConfig(key, str(data[key]))

# 🔧 Replace with your actual file path
file_path = 'creds.py'

def processCreds():
    module = load_module_from_file(file_path)
    constants_dict = extract_class_constants(module)
    save_in_db(constants_dict)

print("start")
print(consts.db.getConfigs())

print("end")