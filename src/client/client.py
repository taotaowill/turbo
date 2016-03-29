# encoding: utf-8
import json
import urllib

from tornado import httpclient

MASTER = "127.0.0.1:8888"


def add_task(task):
    """
    Add task to master
    """
    url = "http://127.0.0.1:8888/add-task?%s" % urllib.urlencode(task)
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(url)
        ret = json.loads(response.body)
        if ret.get("status"):
            return True, ret.get("data")
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    return False, None


def cancel_task(task):
    """
    Add task to master
    """
    url = "http://127.0.0.1:8888/cancel-task?%s" % urllib.urlencode(task)
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(url)
        ret = json.loads(response.body)
        if ret.get("status"):
            return True, ret.get("data")
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    return False, None


def main():
    params = {
        "a": 1,
        "b": 2
    }
    params_json = json.dumps(params)
    task = {
        "name": "calc.sub",
        "version": "0.0.1",
        "params": params_json,
        "interval":  60
        # "timeout": 0,
        # "cron": "*/30 * * * * *"
    }
    status, tid = add_task(task)
    print tid
    pa = {
        "task": tid
    }
    cancel_task(pa)


if __name__ == "__main__":
    main()
