# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest import mock
from shared.user_feedback import UserFeedback
from shared.models.chat_context import (
    ChatContext,
)  # Assuming you have a ChatContext class


class TestUserFeedback:
    @mock.patch("shared.user_feedback.TeamAILogger.analytics")
    def test_on_message_voted(self, teamai_logger_analytics_mock):
        # Arrange
        teamai_logger_analytics_mock.return_value = None
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
        teamai_logger_analytics_mock.assert_called_once()
        teamai_logger_analytics_mock.assert_called_once_with(vote, context.to_dict())
