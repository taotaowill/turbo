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
    url = "%s/cancel-task?task=%s" % (MASTER, urllib.urlencode(task))
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
    #     "url": "http://127.0.0.1:8080/api/turbo-trace/trace-cluster-agent-errors?cluster=/baidu/galaxy",
    # }
    params = {
        "url": "http://127.0.0.1:8080/api/turbo-trace/trace-cluster-agent-states?cluster=/baidu/galaxy",
    }
    params_json = json.dumps(params)
    task = {
        "name": "lumia.trace_lumia_url",
        "version": "0.0.1",
        "params": params_json,
        "interval": 60,
        "timeout": 60,
        # "cron": "*/30 * * * * *"
    }
    status, tid = add_task(task)
    print tid

    # params = {
    #     "a": 10,
    #     "b": 15
    # }
    # params_json = json.dumps(params)
    # task = {
    #     "name": "calc.sub",
    #     "version": "0.0.1",
    #     "params": params_json,
    #     "timeout": 60,
    # }
    # status, tid = add_task(task)
    # print tid


if __name__ == "__main__":
    main()
