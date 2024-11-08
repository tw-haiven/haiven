# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json

from fastapi.responses import FileResponse

from api.boba_api import BobaApi
from config_service import ConfigService
from llms.chats import ChatManager
from logger import HaivenLogger
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client import OAuthError
from jinja2 import Environment, FileSystemLoader
from ui.url import HaivenUrl
import time
import os


class Server:
    boba_build_dir_path = "./resources/static/out"

    def __init__(
        self,
        chat_manager: ChatManager,
        config_service: ConfigService,
        boba_api: BobaApi = None,
    ):
        self.url = HaivenUrl()
        self.chat_manager = chat_manager
        self.config_service = config_service
        self.boba_api = boba_api

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
                self.chat_manager.chat_session_memory.dump_as_text(
                    chat_session_key, user_id
                )
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
        async def backwards_teamai(request: Request):
            # backwards compatibility from when "/teamai" was the main entry path
            return RedirectResponse(url=self.url.analysis())

        @app.get(self.url.analysis())
        async def backwards_analysis(request: Request):
            # backwards compatibility
            return RedirectResponse(url=self.url.boba())

        @app.get(self.url.testing())
        async def backwards_testing(request: Request):
            # backwards compatibility
            return RedirectResponse(url=self.url.boba())

        @app.get(self.url.coding())
        async def backwards_coding(request: Request):
            # backwards compatibility
            return RedirectResponse(url=self.url.boba())

        @app.get(self.url.about())
        async def backwards_about(request: Request):
            # backwards compatibility
            return RedirectResponse(url=self.url.boba() + "/about")

        @app.get(self.url.knowledge())
        async def backwards_knowledge(request: Request):
            # backwards compatibility
            return RedirectResponse(url=self.url.boba() + "/knowledge")

        @app.get(self.url.logout())
        async def logout(request: Request):
            request.session.pop("user", None)
            return RedirectResponse(url="/")

        @app.middleware("http")
        async def boba_middleware(request: Request, call_next):
            allowed_boba_paths = [
                "dashboard",
                "knowledge",
                "knowledge-chat",
                "chat",
                "cards",
                "scenarios",
                "threat-modelling",
                "creative-matrix",
                "requirements",
                "story-validation",
            ]
            paths = request.url.path.split("/")
            if (
                len(paths) >= 2
                and paths[-2] == "boba"
                and paths[-1] in allowed_boba_paths
            ):
                return HTMLResponse(
                    open(f"./{Server.boba_build_dir_path}/{paths[-1]}.html").read()
                )
            return await call_next(request)

        async def check_authentication(request: Request, call_next):
            allowlist = [
                "/",
                "/auth",
                "/login",
                "/logout",
                "/index.html",
                "/static/main.css",
                "/static/social-preview-image.png",
                "/static/thoughtworks_logo_grey.png",
                "/favicon.ico",
            ]

            if request.url.path not in allowlist:
                try:
                    user = request.session.get("user")
                    if not user:
                        return auth_error_response({})
                    return await call_next(request)
                except AssertionError as error:
                    print(f"AssertionError {error}")
                    return auth_error_response(error)
            return await call_next(request)

        @app.middleware("http")
        async def check_oauth2_authentication(request: Request, call_next):
            if os.environ.get("AUTH_SWITCHED_OFF") == "true":
                # TODO: Only allow this if localhost?
                return await call_next(request)
            else:
                return await check_authentication(request, call_next)

        @app.middleware("http")
        async def check_session_expiry(request: Request, call_next):
            session_expiry_seconds = int(
                os.environ.get("SESSION_EXPIRY_SECONDS", 7 * 24 * 60 * 60)
            )  # 1 week

            session = request.session
            current_time = int(time.time())
            if session:
                if "created_at" in session:
                    created_at = session["created_at"]
                    if current_time - created_at > session_expiry_seconds:
                        user = session.get("user", {})
                        user_name = user.get("name", "")
                        HaivenLogger.get().logger.info(
                            f"Session for {user_name} expired due to inactivity of {current_time - created_at} seconds."
                        )
                        request.session.clear()
                        return RedirectResponse(url="/")
                    else:
                        session["created_at"] = current_time
                else:
                    session["created_at"] = current_time

            response = await call_next(request)
            return response

        # Session lifetime is managed by the check_session_expiry middleware
        app.add_middleware(SessionMiddleware, secret_key="!secret", max_age=None)

        oauth = OAuth()

        oauth.register(
            name="oauth",
            client_id=os.getenv("OAUTH_CLIENT_ID"),
            client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
            server_metadata_url=os.getenv("OPENID_CONF_URL"),
            client_kwargs={"scope": "openid email profile"},
        )

        origins = [
            "http://localhost:3000",  # Allow CORS from localhost:3000
        ]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def serve_static_resources(self, app):
        static_dir = Path("./resources/static")
        static_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/static", StaticFiles(directory=static_dir, html=True), name="static"
        )

        @app.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            return FileResponse("./resources/static/favicon.ico")

    def serve_react_frontend(self, app):
        try:
            app.mount(
                "/boba",
                StaticFiles(directory=Path(Server.boba_build_dir_path), html=True),
                name="out",
            )
        except Exception as e:
            print(f"WARNING: Boba UI cannot be mounted {e}")

    def serve_static_from_knowledge_pack(self, app):
        knowledge_pack_path = self.config_service.load_knowledge_pack_path()

        teams_static_dir = Path(knowledge_pack_path + "/static")
        teams_static_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/kp-static",
            StaticFiles(directory=teams_static_dir, html=True),
            name="kp-static",
        )

    def serve_static(self, app):
        self.serve_static_resources(app)
        self.serve_react_frontend(app)
        self.serve_static_from_knowledge_pack(app)

    # FastAPI APP => for authentication and static file serving
    def create(self):
        app = FastAPI()

        self.user_endpoints(app)
        self.serve_static(app)
        self.boba_api.add_endpoints(app)

        return app
