from shared.logger import HaivenLogger


class UserFeedback:
    @staticmethod
    def on_message_voted(vote: str, context: dict):
        HaivenLogger.get().analytics(vote, context)
