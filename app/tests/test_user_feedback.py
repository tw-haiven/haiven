# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest import mock
from shared.user_feedback import UserFeedback
from shared.ui.chat_context import (
    ChatContext,
)  # Assuming you have a ChatContext class


class TestUserFeedback:
    @mock.patch("shared.user_feedback.HaivenLogger.analytics")
    def test_on_message_voted(self, haiven_logger_analytics_mock):
        # Arrange
        haiven_logger_analytics_mock.return_value = None
        vote = "upvote"
        context = ChatContext(
            tab_id="tab_id_test",
            interaction_pattern="interaction_pattern_test",
            model="model_test",
            temperature=0.5,
            prompt="prompt_test",
            message="a message from the llm model",
        )  # Assuming you have a way to create a ChatContext instance

        # Act
        UserFeedback.on_message_voted(vote, context.to_dict())

        # Assert
        haiven_logger_analytics_mock.assert_called_once()
        haiven_logger_analytics_mock.assert_called_once_with(vote, context.to_dict())
