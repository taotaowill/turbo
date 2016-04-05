# encoding: utf-8
"""
@file lumia task
@author wanghaitao01
@date 2016/03/30
"""
import json
from tornado import httpclient
import turbo


@turbo.service(version="0.0.1")
def trace_lumia_url(url):
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
