# encoding: utf-8
import pymongo

# server
PORT = 8880

# mongo
MONGO_CLIENT = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
TURBO_DB = MONGO_CLIENT.turbo
TASK_COLLECTION = TURBO_DB.task
RESULT_COLLECTION = TURBO_DB.result
SERVICE_COLLECTION = TURBO_DB.service

kStatePending = 0
kStateRunning = 1
kStateFinished = 2
