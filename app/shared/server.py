# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import json
from shared.services.config_service import ConfigService
from shared.chats import ServerChatSessionMemory
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client import OAuthError
from jinja2 import Environment, FileSystemLoader
from shared.url import Url
import os


class Server:
    def __init__(self, chat_session_memory: ServerChatSessionMemory):
        self.url = Url()
        self.chat_session_memory = chat_session_memory

    def user_endpoints(self, app):
        jinja_env = Environment(loader=FileSystemLoader("./resources/html_templates"))

        def auth_error_response(error):
            template = jinja_env.get_template("auth_error.html")
            html = template.render(error=error)
            return HTMLResponse(html)

        @app.get("/")
        async def homepage(request: Request):
            if os.environ.get("AUTH_SWITCHED_OFF") == "true":
                return RedirectResponse(url=self.url.analysis())

            user = request.session.get("user")
            json.dumps(user)

            template = jinja_env.get_template("index.html")
            html = template.render(user=user)
            return HTMLResponse(html)

        @app.get("/chat-session")
        async def chat_session(request: Request):
            chat_session_key = request.query_params.get("key")
            user_id = request.session["user"]["sub"]
            return PlainTextResponse(
                self.chat_session_memory.dump_as_text(chat_session_key, user_id)
            )

        @app.get(self.url.login())
        async def login(request: Request):
            redirect_uri = request.url_for("auth")
            return await oauth.oauth.authorize_redirect(request, redirect_uri)

        @app.get(self.url.auth())
        async def auth(request: Request):
            try:
                token = await oauth.oauth.authorize_access_token(request)
            except OAuthError as error:
                return HTMLResponse(f"<h1>{error.error}</h1>")
            user = token.get("userinfo")
            if user:
                request.session["user"] = dict(user)
            return RedirectResponse(url="/")

        @app.get(self.url.general())
        async def teamai(request: Request):
            # backwards compatibility from when "/teamai" was the main entry path
            return RedirectResponse(url=self.url.analysis())

        @app.get(self.url.logout())
        async def logout(request: Request):
            request.session.pop("user", None)
            return RedirectResponse(url="/")

        @app.middleware("http")
        async def check_oauth2_authentication(request: Request, call_next):
            if os.environ.get("AUTH_SWITCHED_OFF") == "true":
                # TODO: Only allow this if localhost?
                return await call_next(request)
            else:
                whitelist = [
                    "/",
                    "/auth",
                    "/login",
                    "/logout",
                    "/index.html",
                    "/static/main.css",
                    "/static/thoughtworks_logo_grey.png",
                ]

                if (
                    "/api/" not in request.url.path
                    and request.url.path not in whitelist
                ):
                    try:
                        user = request.session.get("user")
                        if not user:
                            return auth_error_response({})
                        return await call_next(request)
                    except AssertionError as error:
                        print(f"AssertionError {error}")
                        return auth_error_response(error)
                return await call_next(request)

        app.add_middleware(SessionMiddleware, secret_key="!secret")
        oauth = OAuth()

        oauth.register(
            name="oauth",
            client_id=os.getenv("OAUTH_CLIENT_ID"),
            client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
            server_metadata_url=os.getenv("OPENID_CONF_URL"),
            client_kwargs={"scope": "openid email profile"},
        )

    def serve_static(self, app):
        static_dir = Path("./resources/static")
        static_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/static", StaticFiles(directory=static_dir, html=True), name="static"
        )

        DEFAULT_CONFIG_PATH = "config.yaml"
        data = ConfigService._load_yaml(DEFAULT_CONFIG_PATH)
        knowledge_pack_path = data["knowledge_pack"]["path"]

        teams_static_dir = Path(knowledge_pack_path + "/static")
        teams_static_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/kp-static",
            StaticFiles(directory=teams_static_dir, html=True),
            name="kp-static",
        )

    # FastAPI APP => for authentication and static file serving
    def create(self):
        app = FastAPI()

        self.user_endpoints(app)
        self.serve_static(app)

        return app
