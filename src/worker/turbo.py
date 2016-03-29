# encoding: utf-8
import settings
import json
import datetime


def make_service():
    service_dict = {}

    def version_wrapper(version):
        def name_wrapper(func):
            key = "%s.%s" % (func.__module__.replace(settings.LIB_PREFIX, "", 1), func.__name__)
            service_dict[key] = {
                "module": func.__module__,
                "function": func.__name__,
                "version": version
            }

            def return_wrapper(tid, params, set_state):
                result = func(**params)
                result_str = json.dumps(result)
                settings.RESULT_COLLECTION.insert(
                    {
                        "id": tid,
                        "data": result_str,
                        "created": datetime.datetime.utcnow()
                    }
                )
                state = settings.kStateRunning
                if set_state:
                    state = settings.kStateFinished
                settings.TASK_COLLECTION.update(
                    {
                        "id": tid
                    },
                    {
                        "$set": {
                            "updated": datetime.datetime.utcnow(),
                            "state": state
                        }
                    }
                )
            return return_wrapper
        return name_wrapper
    version_wrapper.all = service_dict
    return version_wrapper

service = make_service()
