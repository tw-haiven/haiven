# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os


class ApiFeatures:
    def __init__(self, app: FastAPI):
        self.app = app
        self.register_endpoints()

    def register_endpoints(self):
        @self.app.get("/api/features")
        async def get_features():
            # Server-side feature toggles
            features = {
                "THOUGHTWORKS": os.getenv("THOUGHTWORKS_INSTANCE", "false").lower()
                == "true",
                "API_KEY_AUTH": os.getenv("API_KEY_AUTH_ENABLED", "false").lower()
                == "true",
            }

            return JSONResponse(content=features)
