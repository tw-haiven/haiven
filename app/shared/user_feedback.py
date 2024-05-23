# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.logger import HaivenLogger


class UserFeedback:
    @staticmethod
    def on_message_voted(vote: str, context: dict):
        HaivenLogger.get().analytics(vote, context)
