# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import json
import sys
from loguru import logger


class TeamAILogger:
    __instance = None

    def __init__(self, loguru_logger):
        print("instantiating TeamAILogger")
        loguru_logger.remove()

        self.logger = loguru_logger.patch(TeamAILogger.patching)
        self.logger.add(sys.stdout, format="{extra[serialized]}")

        self.logger.level("ANALYTICS", no=60)

        if TeamAILogger.__instance is not None:
            raise Exception(
                "TeamAILogger is a singleton class. Use getInstance() to get the instance."
            )
        TeamAILogger.__instance = self

    def analytics(self, message, extra=None):
        self.logger.log("ANALYTICS", message, extra=extra)

    @staticmethod
    def get():
        if TeamAILogger.__instance is None:
            TeamAILogger(logger)
        return TeamAILogger.__instance

    @staticmethod
    def serialize(record):
        subset = {
            "time": str(record["time"]),
            "message": record["message"],
            "level": record["level"].name,
            "file": record["file"].path,
        }
        subset.update(record["extra"])
        return json.dumps(subset)

    @staticmethod
    def patching(record):
        record["extra"]["serialized"] = TeamAILogger.serialize(record)
