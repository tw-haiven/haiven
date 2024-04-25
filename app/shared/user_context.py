# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from gradio import Request


class UserContext:
    _instance = None

    def __init__(self):
        self._context = {}

    @staticmethod
    def get_active_path(request: Request):
        active_path = request.request.headers["referer"].split("/")[-2]
        if active_path not in [
            "analysis",
            "testing",
            "coding",
            "knowledge",
            "about",
            "chat",
        ]:
            return "unknown"
        return active_path

    @staticmethod
    def __get_session_id(request: Request):
        return request.request.session.get("user", {}).get("sub", "guest")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UserContext()
        return cls._instance

    def _get_value(self, session_id, key):
        return self._context.get(session_id, {}).get(key, None)

    def _set_value(self, session_id, key, value):
        if session_id not in self._context:
            self._context[session_id] = {}
        self._context[session_id][key] = value
        return value

    def get_value(self, request: Request, key, app_level=False):
        if app_level:
            session_id = self.__get_session_id(request)
            return self._get_value(session_id, key)
        else:
            active_path = UserContext.get_active_path(request)
            if active_path == "unknown":
                return None
            else:
                session_id = self.__get_session_id(request)
                return self._get_value(session_id, active_path + "_" + key)

    def set_value(self, request: Request, key, value, app_level=False):
        if app_level:
            session_id = self.__get_session_id(request)
            return self._set_value(session_id, key, value)
        else:
            active_path = UserContext.get_active_path(request)
            if active_path != "unknown":
                session_id = self.__get_session_id(request)
                return self._set_value(session_id, active_path + "_" + key, value)

    def get_user_data(self, request: Request):
        return self._context.get(self.__get_session_id(request), {})


user_context = UserContext.get_instance()
