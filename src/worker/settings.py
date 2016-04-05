# encoding: utf-8
import turbo
import os

# endpoint
MASTER = "http://127.0.0.1:8880"
WORKER = "http://127.0.0.1:8881"

# mongodb
turbo.config({
    "MONGODB": "mongodb://127.0.0.1:27017/",
    "LIB_PREFIX": "lib",
    "LIB_PATH": os.path.join(os.path.dirname(__file__), "lib")
})
