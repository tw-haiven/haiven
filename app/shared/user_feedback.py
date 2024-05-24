# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from shared.logger import HaivenLogger


class UserFeedback:
    @staticmethod
    def on_message_voted(vote: str, context: dict):
        HaivenLogger.get().analytics(vote, context)
