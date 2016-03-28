# encoding: utf-8
import json
import threading
import urllib
import uuid

from tornado import httpclient
from tornado import ioloop
import settings

TASK_LIST = []
SERVICE_DICT = {}
RESULT_DICT = {}


def register_service(name, version, func):
    if name in SERVICE_DICT:
        SERVICE_DICT[name][version] = func
    else:
        SERVICE_DICT[name] = {version: func}


def service(func):
    def service_wrapper(tid, params, *args, **kwargs):
        RESULT_DICT[tid] = None
        result = func(params, *args, **kwargs)
        RESULT_DICT[tid] = result
    return service_wrapper


@service
def add(params):
    a = int(params.get("a"))
    b = int(params.get("b"))
    return a + b
register_service("add", "0.0.1", add)


@service
def sub(params):
    a = int(params.get("a"))
    b = int(params.get("b"))
    return a - b
register_service("sub", "0.0.1", sub)


def register_worker():
    """
    Register service to master
    """
    services = [
        {
            "name": "sub",
            "version": "0.0.1"
         },
        {
            "name": "add",
            "version": "0.0.1"
        }
    ]
    params = {
        "worker": settings.WORKER,
        "services": json.dumps(services)
    }
    url = "http://127.0.0.1:8888/register-worker?%s" % urllib.urlencode(params)
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(url)
        print(response.body)
        print("register worker ok")
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    http_client.close()


def run_task(task):
    name = task.get("name")
    version = task.get("version")
    params = task.get("params")

    if name in SERVICE_DICT and version in SERVICE_DICT[name]:
        func = SERVICE_DICT[name][version]
        tid = str(uuid.uuid1())
        t = threading.Thread(target=func, args=(tid, params))
        t.start()
        t.join()
        print "get result %s" % RESULT_DICT[tid]


def poll_task():
    params = {
        "worker": settings.WORKER
    }
    url = "http://127.0.0.1:8888/fetch-task?%s" % urllib.urlencode(params)
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(url, request_timeout=30000)
        ret = json.loads(response.body)
        if ret.get("status"):
            task = ret.get("data")
            print("get task from master %s" % task.get("id"))
            run_task(task)
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    http_client.close()


def main():
    register_worker()
    task_timer = ioloop.PeriodicCallback(poll_task, 5000)
    task_timer.start()
    ioloop.IOLoop.current().start()


if "__main__" == __name__:
    main()

