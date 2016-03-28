# encoding: utf-8
import json
import urllib
from tornado import httpclient


MASTER = "127.0.0.1:8888"


def add_task():
    params = {
        "a": 1,
        "b": 2
    }
    params_json = json.dumps(params)
    p = {
        "name": "add",
        "version": "0.0.1",
        "params": params_json
    }

    url = "http://127.0.0.1:8888/add-task?%s" % urllib.urlencode(p)
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(url)
        print response.body
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    http_client.close()


def main():
    add_task()


if __name__ == "__main__":
    main()
