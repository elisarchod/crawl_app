import os
from functools import wraps
from threading import Lock

RESOURCES_DIRECTORY = 'resources'
os.makedirs(RESOURCES_DIRECTORY, exist_ok=True)

def singleton(cls):
    instances = {}
    lock = Lock()
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance 

