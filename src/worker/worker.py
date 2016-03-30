# encoding: utf-8
"""
@file turbo worker
@author wanghaitao01
@date 2016/03/29
"""
import json
import os
import sys
import time
import threading
import urllib

from tornado import httpclient
from tornado import ioloop

import settings
import turbo

SERVICE_DICT = {}
SERVICE_LIST = []


def check_task_valid(tid):
    """
    Whether task is still enable or canceled
    """
    task = settings.TASK_COLLECTION.find_one({"id": tid})
    if not task or task.get("canceled"):
        return False
    return True


def set_task_state(tid, state):
    """
    Set task state
    """
    settings.TASK_COLLECTION.update(
        {"id": tid},
        {
            "$set": {
                "state": state
            }
        })


def register_worker():
    """
    Register service to master
    """
    params = {
        "worker": settings.WORKER,
        "services": json.dumps(SERVICE_LIST)
    }
    url = "%s/register-worker?%s" % (settings.MASTER, urllib.urlencode(params))
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


def restore_task(tid):
    """
    Restore task state to pending
    """
    print("restore task %s state to pending" % tid)
    return 0


def run_task_thread(func, tid, params, interval):
    set_state = True
    if interval > 0:
        set_state = False
        while check_task_valid(tid):
            t = threading.Thread(target=func, args=(tid, params, set_state))
            t.start()
            t.join()
            time.sleep(interval)
    else:
        t = threading.Thread(target=func, args=(tid, params, set_state))
        t.start()
        t.join()
    # set task state to finished
    set_task_state(tid, settings.kStateFinished)
    print("task %s run over" % tid)


def run_task(task):
    """
    Run task
    """
    tid = task.get("id")
    name = task.get("name")
    version = task.get("version")
    params = task.get("params")

    if name in SERVICE_DICT and version in SERVICE_DICT[name]:
        func = SERVICE_DICT[name][version]
        print("task %s run begin" % tid)
        interval = task.get("interval", 0)
        t = threading.Thread(target=run_task_thread, args=(func, tid, params, interval,))
        t.start()
    else:
        print("specific func does not exist in this worker")
        restore_task(tid)


def fetch_task():
    """
    Fetch one task from master
    """
    params = {"worker": settings.WORKER}
    url = "%s/fetch-task?%s" % (settings.MASTER, urllib.urlencode(params))
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


def load_libs():
    """
    Load worker custom libs
    """
    for _, _, file_names in os.walk(settings.LIB_PATH):
        for file_name in file_names:
            module, ext = os.path.splitext(os.path.basename(file_name))
            module = settings.LIB_PREFIX + module
            __import__(module)

    # fill into SERVICE_DICT and SERVICE_LIST
    for name, func_dict in turbo.service.all.items():
        version = func_dict.get("version")
        module_name = func_dict.get("module")
        function_name = func_dict.get("function")
        func = getattr(sys.modules.get(module_name), function_name)
        SERVICE_DICT[name] = {version: func}
        SERVICE_LIST.append({
            "name": name,
            "version": version
        })


def main():
    """
    Worker main
    """
    load_libs()
    register_worker()

    task_timer = ioloop.PeriodicCallback(fetch_task, 1000)
    task_timer.start()
    ioloop.IOLoop.current().start()


if "__main__" == __name__:
    main()
