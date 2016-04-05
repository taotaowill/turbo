# encoding: utf-8
import json
import datetime
import os

import pymongo

# task state
TASK_STATE_PENDING = 0
TASK_STATE_RUNNING = 1
TASK_STATE_STOPPED = 2

# lib path
LIB_PREFIX = "lib"
LIB_PATH = os.path.join(os.path.dirname(__file__), LIB_PREFIX)

# mongodb
MONGODB = "mongodb://127.0.0.1:27017/"
MONGODB_CLIENT = pymongo.MongoClient(MONGODB)
DATABASE = MONGODB_CLIENT["turbo"]
TASK = DATABASE.task
RESULT = DATABASE.result
SERVICE = DATABASE.service


def make_service():
    service_dict = {}

    def version_wrapper(version):
        def name_wrapper(func):
            key = "%s.%s" % (func.__module__.replace(LIB_PREFIX + ".", "", 1), func.__name__)
            service_dict[key] = {
                "module": func.__module__,
                "function": func.__name__,
                "version": version
            }

            def return_wrapper(tid, params, set_state):
                result = func(**params)
                result_str = json.dumps(result)
                RESULT.insert(
                    {
                        "id": tid,
                        "data": result_str,
                        "created": datetime.datetime.now()
                    }
                )
                state = TASK_STATE_RUNNING
                if set_state:
                    state = TASK_STATE_STOPPED
                TASK.update(
                    {
                        "id": tid
                    },
                    {
                        "$set": {
                            "updated": datetime.datetime.now(),
                            "state": state
                        }
                    }
                )
            return return_wrapper
        return name_wrapper
    version_wrapper.all = service_dict
    return version_wrapper

service = make_service()


def config(opt):
    global LIB_PREFIX
    global LIB_PATH
    global MONGODB
    global MONGODB_CLIENT
    global DATABASE
    global TASK
    global RESULT
    global SERVICE

    LIB_PREFIX = opt.get("LIB_PREFIX") or LIB_PREFIX
    LIB_PATH = opt.get("LIB_PATH") or os.path.join(os.path.dirname(__file__), LIB_PREFIX)
    MONGODB = opt.get("MONGODB") or MONGODB
    MONGODB_CLIENT = pymongo.MongoClient(MONGODB)
    DATABASE = opt.get("DATABASE") or DATABASE
    TASK = DATABASE.task
    RESULT = DATABASE.result
    SERVICE = DATABASE.service
