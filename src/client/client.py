# encoding: utf-8
import json
import urllib

from tornado import httpclient

MASTER = "http://127.0.0.1:8880"


def add_task(task):
    """
    Add task to master
    """
    url = "%s/add-task?%s" % (MASTER, urllib.urlencode(task))
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
    url = "%s/cancel-task?%s" % (MASTER, urllib.urlencode(task))
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
    # params = {
    #     "url": "http://www.baidu.com",
    # }
    # params_json = json.dumps(params)
    # task = {
    #     "name": "lumia.trace_operate",
    #     "version": "0.0.1",
    #     "params": params_json,
    #     "interval":  10
    #     # "timeout": 0,
    #     # "cron": "*/30 * * * * *"
    # }
    # status, tid = add_task(task)
    # # print tid
    pa = {
        "task": "95fdd35a-f674-11e5-bebf-54ee7523d60e"
    }
    cancel_task(pa)


if __name__ == "__main__":
    main()
