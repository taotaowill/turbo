# encoding: utf-8
import json
import uuid
import tornado.ioloop
import tornado.web
import settings

TASK_LIST = []
TASK_DICT = {}
WORKER_DICT = {}


class AddTask(tornado.web.RequestHandler):
    """
    Client add task
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
            "params": json.loads(self.get_argument('params'))
        }
        TASK_LIST.append(task)
        self.write(json.dumps(ret))


class FetchTask(tornado.web.RequestHandler):
    """
    Fetch one task from task queue
    """
    def get(self):
        ret = {
            "status": True,
            "message": "ok",
            "data": None
        }
        worker_id = self.get_argument("worker")
        service_map = WORKER_DICT.get(worker_id)
        target = None
        for task in TASK_LIST:
            tag = "%s#%s" % (task["name"], task["version"])
            if tag in service_map.keys():
                TASK_DICT[task["id"]] = {
                    "worker": worker_id,
                    "state": "running"
                }
                TASK_LIST.remove(task)
                target = task
                break
        if target is None:
            ret["status"] = False
            ret["message"] = "no suitable tasks"
        else:
            ret["data"] = target
        self.write(json.dumps(ret))


class RegisterWorker(tornado.web.RequestHandler):
    """
    Register worker
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
            service_dict[tag] = service
        WORKER_DICT[worker_id] = service_dict
        self.write(json.dumps(ret))


def make_app():
    return tornado.web.Application([
        (r"/add-task", AddTask),
        (r"/fetch-task", FetchTask),
        (r"/register-worker", RegisterWorker),
    ])


# def check():
#     print "hello"


if __name__ == "__main__":
    app = make_app()
    app.listen(settings.PORT)
    # # worker death checker
    # death_checker = tornado.ioloop.PeriodicCallback(check, 1000)
    # death_checker.start()
    tornado.ioloop.IOLoop.current().start()
