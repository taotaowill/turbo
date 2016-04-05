# encoding: utf-8
"""
@file turbo master
@author wanghaitao01
@date 2016/03/29
"""
import datetime
import json
import logging
import logging.handlers
import os
import uuid

from bson import json_util
import tornado.ioloop
import tornado.web

import settings
import turbo


LOGGER = logging.getLogger('master')


def init_log():
    """
    Init log
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(asctime)s %(module)s:%(lineno)s %(process)d %(message)s',
        filename='master.log',
        filemode='w')
    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(module)s:%(lineno)s %(process)d %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger('master').addHandler(console)


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
            "state": turbo.TASK_STATE_PENDING,
            "created": datetime.datetime.utcnow(),
            "updated": datetime.datetime.utcnow(),
            "interval": int(self.get_argument('interval', 0)),
            "timeout": int(self.get_argument('timeout', 0)),
            "time": self.get_argument("time", None)
        }
        turbo.TASK.insert(task)
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
        turbo.TASK.update(
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
        services = turbo.SERVICE.find_one({"id": worker_id})
        if not services:
            ret["status"] = False
            ret["message"] = "worker not registered yet"
        else:
            service_dict = services["services"]
            target = None
            tasks = turbo.TASK.find({
                "state": turbo.TASK_STATE_PENDING,
                "canceled": {
                    "$ne": True
                }
            })
            for task in tasks:
                tag = "%s#%s" % (task["name"], task["version"])
                tag = tag.replace(".", "_")
                if tag in service_dict.keys():
                    turbo.TASK.update(
                        {"id": task["id"]},
                        {
                            "$set": {
                                "state": turbo.TASK_STATE_RUNNING,
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


class Dashboard(tornado.web.RequestHandler):
    """
    Show all task info
    """
    def get(self):
        # ret = {
        #     "status": True,
        #     "message": "ok",
        #     "data": {}
        # }
        # tasks = turbo.TASK.find()
        # services = turbo.SERVICE.find()
        # ret["data"]["tasks"] = tasks
        # ret["data"]["services"] = services
        # self.write(json_util.dumps(ret))
        tasks = turbo.TASK.find()
        services = turbo.SERVICE.find()
        self.render("index.html", tasks=tasks, services=services)


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
        turbo.SERVICE.update(
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
        (r"/$", Dashboard),
    ])


def running_check():
    """
    Check running task, switch state of timeout task
    """
    tasks = turbo.TASK.find({
        "state": turbo.TASK_STATE_RUNNING,
        "canceled": {"$ne": True}
    })
    now = datetime.datetime.utcnow()
    for task in tasks:
        timeout = task.get("timeout")
        if not timeout:
            continue
        updated = task["updated"]
        expired = updated + datetime.timedelta(seconds=task["timeout"])
        if now > expired:
            turbo.TASK.update(
                {
                    "id": task["id"]
                },
                {
                    "$set": {
                        "updated": datetime.datetime.utcnow(),
                        "state": turbo.TASK_STATE_PENDING
                    }
                }
            )
            LOGGER.info("task %s switch state to pending" % task["id"])


if __name__ == "__main__":
    init_log()
    app = make_app()
    app.listen(settings.PORT)

    # running task checker
    running_checker = tornado.ioloop.PeriodicCallback(running_check, 10000)
    running_checker.start()

    LOGGER.info("turbo master start...")
    tornado.ioloop.IOLoop.current().start()
    LOGGER.info("turbo master exit.")
