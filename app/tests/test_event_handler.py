from shared.event_handler import EventHandler
from unittest.mock import MagicMock, patch, PropertyMock


class TestEventHandler:
    def test_on_ui_load(self):
        # Setup
        request = MagicMock()
        url = "http://localhost:7860/teamai"
        request.url = url
        sub = "123"
        request.request = MagicMock()
        session = {"user": {"sub": sub}}
        request.request.session = session
        logger = MagicMock()
        logger.analytics = MagicMock()
        logger_factory = MagicMock()
        logger_factory.get.return_value = logger

        event_handler = EventHandler(logger_factory)

        # Action
        event_handler.on_ui_load(request)

        # Assert
        logger.analytics.assert_called_with(f"User {sub} loaded UI at {url}")

    @patch("shared.event_handler.gr.Tabs")
    def test_on_ui_load_with_tab_deeplink(self, mock_tabs):
        # Setup
        url = "http://localhost:7860/teamai?tab=analysis"
        sub = "123"
        session = {"user": {"sub": sub}}
        nested_request = MagicMock()
        type(nested_request).session = PropertyMock(return_value=session)
        request = MagicMock()
        type(request).url = PropertyMock(return_value=url)
        type(request).request = nested_request
        logger = MagicMock()
        logger.analytics = MagicMock()
        logger_factory = MagicMock()
        logger_factory.get.return_value = logger
        tab_selection = MagicMock()
        mock_tabs.return_value = tab_selection

        event_handler = EventHandler(logger_factory)

        # Action
        returned_tabs, user_state = event_handler.on_ui_load_with_tab_deeplink(request)

        # Assert
        logger.analytics.assert_called_with(f"User {sub} loaded UI at {url}")

        assert returned_tabs == tab_selection
        assert user_state == sub

    @patch("shared.event_handler.gr.Tabs")
    def test_on_ui_load_with_tab_deeplink_with_tab_in_query_params(self, mock_tabs):
        # Setup
        request = MagicMock()
        url = "http://localhost:7860/teamai?tab=analysis"
        request.url = url
        tab = "analysis"
        request.query_params = {"tab": tab}
        sub = "123"
        request.request = MagicMock()
        session = {"user": {"sub": sub}}
        request.request.session = session
        logger = MagicMock()
        logger.analytics = MagicMock()
        logger_factory = MagicMock()
        logger_factory.get.return_value = logger
        tab_selection = MagicMock()
        mock_tabs.return_value = tab_selection

        event_handler = EventHandler(logger_factory)

        # Action
        returned_tabs = event_handler.on_ui_load_with_tab_deeplink(request)

        # Assert
        logger.analytics.assert_called_with(f"User {sub} loaded UI at {url}")
        mock_tabs.assert_called_with(selected=tab)
        assert returned_tabs == tab_selection
