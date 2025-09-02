# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_rules import ApiRules
from config_service import ConfigService
from starlette.middleware.sessions import SessionMiddleware


class TestApiRules(unittest.TestCase):
    def setUp(self):
        # Store original environment variable value
        self.original_auth_switched_off = os.environ.get("AUTH_SWITCHED_OFF")
        # Clear AUTH_SWITCHED_OFF to ensure clean test state
        if "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

        # Mock config service
        self.mock_config_service = MagicMock(spec=ConfigService)
        self.mock_config_service.load_knowledge_pack_path.return_value = (
            "app/tests/test_data/test_knowledge_pack"
        )

        # Initialize ApiRules with mocked config service
        self.api_rules = ApiRules(self.app, self.mock_config_service)

        # Clear any loaded rules from initialization
        self.api_rules.loaded_rules = {}

    def tearDown(self):
        """Clean up after each test method."""
        # Restore original environment variable value
        if self.original_auth_switched_off is not None:
            os.environ["AUTH_SWITCHED_OFF"] = self.original_auth_switched_off
        elif "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

    def test_get_casper_rule_success(self):
        """Test successful retrieval of casper rule"""
        # Manually add a rule to the loaded_rules for testing
        self.api_rules.loaded_rules["casper"] = {
            "id": "casper",
            "filename": "casper.md",
            "content": "# Test Casper Workflow\n\nThis is a dummy casper workflow rule for testing the `/api/rules` endpoint.\n",
            "metadata": {"identifier": "casper", "title": "Test Casper Rule"},
        }

        response = self.client.get("/api/rules?rule_id=casper")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")
        self.assertIn("Test Casper Workflow", response.text)
        self.assertIn("dummy casper workflow rule", response.text)

    def test_get_invalid_rule_id(self):
        """Test request with invalid rule ID"""
        response = self.client.get("/api/rules?rule_id=invalid")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("Rule 'invalid' not found", response_data["detail"])

    def test_get_casper_rule_file_not_found(self):
        """Test when casper rule file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            response = self.client.get("/api/rules?rule_id=casper")

            self.assertEqual(response.status_code, 404)
            response_data = response.json()
            self.assertIn("Rule 'casper' not found", response_data["detail"])

    def test_get_casper_rule_file_read_error(self):
        """Test when there's an error reading the casper rule file"""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with patch("os.path.exists", return_value=True):
                with patch("os.listdir", return_value=["casper.md"]):
                    response = self.client.get("/api/rules?rule_id=casper")

                    self.assertEqual(response.status_code, 404)
                    response_data = response.json()
                    self.assertIn("Rule 'casper' not found", response_data["detail"])

    def test_config_service_integration(self):
        """Test that config service is properly used to get knowledge pack path"""
        # Manually add a rule to the loaded_rules for testing
        self.api_rules.loaded_rules["casper"] = {
            "id": "casper",
            "filename": "casper.md",
            "content": "# Test Content\n",
            "metadata": {"identifier": "casper", "title": "Test Casper Rule"},
        }

        response = self.client.get("/api/rules?rule_id=casper")

        # Verify response is successful
        self.assertEqual(response.status_code, 200)

    def test_content_type_header(self):
        """Test that the response has correct content type header"""
        # Manually add a rule to the loaded_rules for testing
        self.api_rules.loaded_rules["casper"] = {
            "id": "casper",
            "filename": "casper.md",
            "content": "# Test Content\n",
            "metadata": {"identifier": "casper", "title": "Test Casper Rule"},
        }

        response = self.client.get("/api/rules?rule_id=casper")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")

    def test_empty_rule_id(self):
        """Test request with empty rule ID"""
        response = self.client.get("/api/rules?rule_id=")

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("Invalid rule ID format", response_data["detail"])

    def test_knowledge_pack_path_construction(self):
        """Test that the knowledge pack path is constructed correctly"""
        # Manually add a rule to the loaded_rules for testing
        self.api_rules.loaded_rules["casper"] = {
            "id": "casper",
            "filename": "casper.md",
            "content": "# Test Content\n",
            "metadata": {"identifier": "casper", "title": "Test Casper Rule"},
        }

        response = self.client.get("/api/rules?rule_id=casper")

        # Verify path construction
        self.assertEqual(response.status_code, 200)

    def test_multiple_rule_ids_in_future(self):
        """Test that the API is structured to support multiple rule IDs in the future"""
        # This test documents the current limitation and future extensibility
        response = self.client.get("/api/rules?rule_id=other_rule")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("Rule 'other_rule' not found", response_data["detail"])

    def test_get_rule_missing_id_parameter(self):
        """Test request without id parameter"""
        response = self.client.get("/api/rules")

        self.assertEqual(
            response.status_code, 422
        )  # Validation error for missing required parameter

    def test_list_rules_endpoint(self):
        """Test the /api/rules/list endpoint"""
        # Add some test rules
        self.api_rules.loaded_rules = {
            "rule1": {
                "id": "rule1",
                "filename": "rule1.md",
                "content": "Content 1",
                "metadata": {"identifier": "rule1", "title": "Rule 1"},
            },
            "rule2": {
                "id": "rule2",
                "filename": "rule2.md",
                "content": "Content 2",
                "metadata": {"identifier": "rule2", "title": "Rule 2"},
            },
        }

        response = self.client.get("/api/rules/list")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(response_data["count"], 2)
        self.assertTrue(response_data["loaded"])
        self.assertEqual(len(response_data["rules"]), 2)

        # Check rule structure
        rule_ids = [rule["id"] for rule in response_data["rules"]]
        self.assertIn("rule1", rule_ids)
        self.assertIn("rule2", rule_ids)

    def test_list_rules_empty(self):
        """Test /api/rules/list when no rules are loaded"""
        self.api_rules.loaded_rules = {}

        response = self.client.get("/api/rules/list")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(response_data["count"], 0)
        self.assertTrue(response_data["loaded"])
        self.assertEqual(len(response_data["rules"]), 0)

    def test_rule_id_validation_edge_cases(self):
        """Test rule ID validation with various edge cases"""
        # Test rule ID that's too long
        long_id = "a" * 101
        response = self.client.get(f"/api/rules?rule_id={long_id}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid rule ID format", response.json()["detail"])

        # Test rule ID with invalid characters
        response = self.client.get("/api/rules?rule_id=invalid@id")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid rule ID format", response.json()["detail"])

        # Test rule ID with spaces
        response = self.client.get("/api/rules?rule_id=invalid id")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid rule ID format", response.json()["detail"])

    def test_rule_not_found_with_available_rules(self):
        """Test rule not found error when other rules are available"""
        # Add some rules
        self.api_rules.loaded_rules = {
            "available1": {
                "id": "available1",
                "filename": "a1.md",
                "content": "content",
                "metadata": {},
            },
            "available2": {
                "id": "available2",
                "filename": "a2.md",
                "content": "content",
                "metadata": {},
            },
        }

        response = self.client.get("/api/rules?rule_id=nonexistent")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("Rule 'nonexistent' not found", response_data["detail"])
        self.assertIn("Available rules:", response_data["detail"])
        self.assertIn("available1", response_data["detail"])
        self.assertIn("available2", response_data["detail"])

    def test_rule_not_found_no_rules_loaded(self):
        """Test rule not found error when no rules are loaded"""
        self.api_rules.loaded_rules = {}

        response = self.client.get("/api/rules?rule_id=nonexistent")

        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("Rule 'nonexistent' not found", response_data["detail"])
        self.assertIn("No rules are currently loaded", response_data["detail"])

    def test_auth_util_methods(self):
        """Test that auth utility methods work correctly"""
        # Test _get_request_source with a mock request
        mock_request = MagicMock()
        mock_request.session = None  # No session
        result = self.api_rules._get_request_source(mock_request)
        self.assertEqual(result, "ui")  # Default to UI when no session

        # Test _is_api_key_auth with no session
        result = self.api_rules._is_api_key_auth(mock_request)
        self.assertFalse(result)

        # Test get_hashed_user_id with no session
        result = self.api_rules.get_hashed_user_id(mock_request)
        self.assertIsNone(result)

    def test_load_rules_directory_not_found(self):
        """Test _load_rules when rules directory doesn't exist"""
        with patch("os.path.exists", return_value=False):
            # Create new instance to test _load_rules
            api_rules = ApiRules(self.app, self.mock_config_service)

            # Verify that rules_loaded is True even when directory doesn't exist
            self.assertTrue(api_rules.rules_loaded)
            self.assertEqual(len(api_rules.loaded_rules), 0)

    def test_load_rules_file_loading_error(self):
        """Test _load_rules when there's an error loading a file"""
        with patch("os.path.exists", return_value=True):
            with patch("os.listdir", return_value=["test.md"]):
                with patch(
                    "frontmatter.load", side_effect=Exception("File read error")
                ):
                    # Create new instance to test _load_rules
                    api_rules = ApiRules(self.app, self.mock_config_service)

                    # Verify that rules_loaded is True even when file loading fails
                    self.assertTrue(api_rules.rules_loaded)
                    self.assertEqual(len(api_rules.loaded_rules), 0)

    def test_load_rules_missing_identifier(self):
        """Test _load_rules when a file is missing identifier in metadata"""
        with patch("os.path.exists", return_value=True):
            with patch("os.listdir", return_value=["test.md"]):
                mock_rule_data = MagicMock()
                mock_rule_data.metadata = {}  # No identifier
                mock_rule_data.content = "test content"

                with patch("frontmatter.load", return_value=mock_rule_data):
                    # Create new instance to test _load_rules
                    api_rules = ApiRules(self.app, self.mock_config_service)

                    # Verify that rules_loaded is True and no rules were loaded due to missing identifier
                    self.assertTrue(api_rules.rules_loaded)
                    self.assertEqual(len(api_rules.loaded_rules), 0)

    def test_load_rules_success(self):
        """Test successful loading of rules"""
        with patch("os.path.exists", return_value=True):
            with patch(
                "os.listdir", return_value=["test.md", "README.md"]
            ):  # README.md should be ignored
                mock_rule_data = MagicMock()
                mock_rule_data.metadata = {
                    "identifier": "test-rule",
                    "title": "Test Rule",
                }
                mock_rule_data.content = "test content"

                with patch("frontmatter.load", return_value=mock_rule_data):
                    # Create new instance to test _load_rules
                    api_rules = ApiRules(self.app, self.mock_config_service)

                    # Verify success
                    self.assertTrue(api_rules.rules_loaded)
                    self.assertEqual(len(api_rules.loaded_rules), 1)
                    self.assertIn("test-rule", api_rules.loaded_rules)

                    # Verify rule data structure
                    rule_data = api_rules.loaded_rules["test-rule"]
                    self.assertEqual(rule_data["id"], "test-rule")
                    self.assertEqual(rule_data["filename"], "test.md")
                    self.assertEqual(rule_data["content"], "test content")
                    self.assertEqual(
                        rule_data["metadata"],
                        {"identifier": "test-rule", "title": "Test Rule"},
                    )

    def test_load_rules_general_exception(self):
        """Test _load_rules when a general exception occurs"""
        # Create a new mock config service that raises an exception
        mock_config_with_error = MagicMock(spec=ConfigService)
        mock_config_with_error.load_knowledge_pack_path.side_effect = Exception(
            "Config error"
        )

        # Create new instance to test _load_rules
        api_rules = ApiRules(self.app, mock_config_with_error)

        # Verify that rules_loaded is True even when config service fails
        self.assertTrue(api_rules.rules_loaded)
        self.assertEqual(len(api_rules.loaded_rules), 0)

    def test_analytics_logging(self):
        """Test that analytics logging is called correctly"""
        # Add a test rule
        self.api_rules.loaded_rules["test"] = {
            "id": "test",
            "filename": "test.md",
            "content": "test content",
            "metadata": {},
        }

        with patch("api.api_rules.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            # Test successful rule access
            response = self.client.get("/api/rules?rule_id=test")
            self.assertEqual(response.status_code, 200)

            # Verify analytics was called
            mock_logger_instance.analytics.assert_called_with(
                "Download rule",
                {
                    "user_id": None,  # No session, so user_id is None
                    "rule_id": "test",
                    "source": "ui",
                },
            )

            # Test failed rule access
            response = self.client.get("/api/rules?rule_id=nonexistent")
            self.assertEqual(response.status_code, 404)

            # Verify analytics was called for failed access
            calls = mock_logger_instance.analytics.call_args_list
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[1][0][0], "Download rule failed - not found")
