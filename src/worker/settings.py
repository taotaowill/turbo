# encoding: utf-8
import os
import pymongo

# endpoint
MASTER = "http://127.0.0.1:8880"
WORKER = "http://127.0.0.1:8881"

# mongodb
MONGO_CLIENT = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
TURBO_DB = MONGO_CLIENT.turbo
TASK_COLLECTION = TURBO_DB.task
RESULT_COLLECTION = TURBO_DB.result

# task state
kStatePending = 0
kStateRunning = 1
kStateFinished = 2

# libs
LIB_PREFIX = "lib."
LIB_PATH = os.path.join(os.path.dirname(__file__), "./lib")

