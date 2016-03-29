# encoding: utf-8
"""
@file turbo master
@author wanghaitao01
@date 2016/03/29
"""
import datetime
import json
import logging
from logging import handlers
import uuid

from bson import json_util
import tornado.ioloop
import tornado.web

import settings

LOGGER = logging.getLogger('master')


def init_log():
    """
    Init log
    """
    global LOGGER
    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(module)s:%(lineno)s %(process)d %(message)s')
    file_handler = handlers.RotatingFileHandler(
        "master.log", maxBytes=20*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)
    LOGGER.setLevel(logging.DEBUG)


class AddTask(tornado.web.RequestHandler):
    """
    Client add task handler
    """
    def get(self):
        ret = {
            "status": True,
            "message": "ok",
            "data": None
        }
        task = {
            "id": str(uuid.uuid1()),
            "name": self.get_argument('name'),
            "version": self.get_argument('version'),
            "params": json.loads(self.get_argument('params')),
            "state": settings.kStatePending,
            "created": datetime.datetime.utcnow(),
            "updated": datetime.datetime.utcnow(),
            "interval": int(self.get_argument('interval', 0)),
            "timeout": int(self.get_argument('timeout', 0)),
            "time": self.get_argument("time", None)
        }
        settings.TASK_COLLECTION.insert(task)
        ret["data"] = task["id"]
        LOGGER.info("task %s added ok, task:\n%s" % (task["id"], task))
        self.write(json_util.dumps(ret))


class CancelTask(tornado.web.RequestHandler):
    """
    Client cancel task handler
    """
    def get(self):
        ret = {
            "status": True,
            "message": "ok",
            "data": None
        }
        tid = self.get_argument("task")
        settings.TASK_COLLECTION.update(
            {"id": tid},
            {
                "$set": {
                    "canceled": True
                }
            }
        )
        LOGGER.info("task %s canceled ok" % tid)
        self.write(json_util.dumps(ret))


class FetchTask(tornado.web.RequestHandler):
    """
    Worker fetch task handler
    """
    def get(self):
        ret = {
            "status": True,
            "message": "ok",
            "data": None
        }
        worker_id = self.get_argument("worker")
        services = settings.SERVICE_COLLECTION.find_one({"id": worker_id})
        if not services:
            ret["status"] = False
            ret["message"] = "worker not registered yet"
        else:
            service_dict = services["services"]
            target = None
            tasks = settings.TASK_COLLECTION.find({"state": settings.kStatePending})
            for task in tasks:
                tag = "%s#%s" % (task["name"], task["version"])
                tag = tag.replace(".", "_")
                if tag in service_dict.keys():
                    settings.TASK_COLLECTION.update(
                        {"id": task["id"]},
                        {
                            "$set": {
                                "state": settings.kStateRunning,
                                "updated": datetime.datetime.utcnow()
                            }
                        },
                        True,
                        False
                    )
                    target = task
                    LOGGER.info("worker %s fetched task %s" % (worker_id, task["id"]))
                    break
            if target is None:
                ret["status"] = False
                ret["message"] = "no suitable tasks"
            else:
                ret["data"] = target
        self.write(json_util.dumps(ret))


class RegisterWorker(tornado.web.RequestHandler):
    """
    Worker register service handler
    """
    def get(self):
        ret = {
            "status": True,
            "message": "ok",
            "data": None
        }
        worker_id = self.get_argument("worker")
        services_str = self.get_argument("services")
        services = json.loads(services_str)
        service_dict = {}
        for service in services:
            tag = "%s#%s" % (service["name"], service["version"])
            tag = tag.replace(".", "_")
            service_dict[tag] = service
        settings.SERVICE_COLLECTION.update(
            {
                "id": worker_id
            },
            {
                "$set": {
                    "id": worker_id,
                    "services": service_dict,
                    "updated": datetime.datetime.utcnow()
                }
            },
            True,
            False
        )
        LOGGER.info("worker %s registered ok, services:\n%s" % (worker_id, services_str))
        self.write(json_util.dumps(ret))


def make_app():
    """
    Master router mapping
    """
    return tornado.web.Application([
        (r"/add-task", AddTask),
        (r"/cancel-task", CancelTask),
        (r"/fetch-task", FetchTask),
        (r"/register-worker", RegisterWorker),
    ])


def running_check():
    """
    Check running task, switch state of timeout task
    """
    tasks = settings.TASK_COLLECTION.find({"state": settings.kStateRunning})
    now = datetime.datetime.utcnow()
    for task in tasks:
        timeout = task.get("timeout")
        if not timeout:
            continue
        updated = task["updated"]
        expired = updated + datetime.timedelta(seconds=task["timeout"])
        if now > expired:
            settings.TASK_COLLECTION.update(
                {
                    "id": task["id"]
                },
                {
                    "$set": {
                        "updated": datetime.datetime.utcnow(),
                        "state": settings.kStatePending
                    }
                }
            )
            LOGGER.info("task %s switch state to pending" % task[id])


if __name__ == "__main__":
    init_log()
    app = make_app()
    app.listen(settings.PORT)

    # running task checker
    running_checker = tornado.ioloop.PeriodicCallback(running_check, 10000)
    running_checker.start()

    tornado.ioloop.IOLoop.current().start()
