# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import PlainTextResponse
import os
import frontmatter
import re
from logger import HaivenLogger
from loguru import logger
from config_service import ConfigService
from auth import auth_util


class ApiRules:
    def __init__(self, app: FastAPI, config_service: ConfigService):
        self.app = app
        self.config_service = config_service
        self.rules_loaded = False
        self.loaded_rules = {}
        self._load_rules()
        self._add_rules_endpoints()

    def _load_rules(self):
        """Load all rules from the rules directory, following the same pattern as prompts."""
        try:
            knowledge_pack_path = self.config_service.load_knowledge_pack_path()
            rules_dir = os.path.join(knowledge_pack_path, "prompts", "rules")

            if not os.path.exists(rules_dir):
                HaivenLogger.get().error(f"Rules directory not found: {rules_dir}")
                self.rules_loaded = True
                return

            # Load all .md files from the rules directory (same pattern as prompts)
            rule_files = sorted(
                [
                    f
                    for f in os.listdir(rules_dir)
                    if f.endswith(".md") and f != "README.md"
                ]
            )

            for filename in rule_files:
                rule_file_path = os.path.join(rules_dir, filename)
                try:
                    # Use frontmatter.load() like prompts do
                    rule_data = frontmatter.load(rule_file_path)

                    # Get rule ID from metadata identifier field, just like prompts do
                    rule_id = rule_data.metadata.get("identifier")
                    if not rule_id:
                        HaivenLogger.get().error(
                            f"Rule file {filename} missing 'identifier' in metadata, skipping"
                        )
                        continue

                    # Store the rule data
                    self.loaded_rules[rule_id] = {
                        "id": rule_id,
                        "filename": filename,
                        "content": rule_data.content,
                        "metadata": rule_data.metadata,
                    }
                except Exception as e:
                    HaivenLogger.get().error(
                        f"Error loading rule file {filename}: {str(e)}"
                    )
                    continue

            self.rules_loaded = True
            HaivenLogger.get().info(
                f"Successfully loaded {len(self.loaded_rules)} rules from {rules_dir}"
            )

        except Exception as e:
            HaivenLogger.get().error(f"Error loading rules: {str(e)}")
            self.rules_loaded = True  # Continue with empty rules

    def _get_request_source(self, request: Request) -> str:
        """Get the source of the request (mcp, ui, or unknown)."""
        return auth_util.get_request_source(request)

    def _is_api_key_auth(self, request: Request) -> bool:
        """Check if the request is using API key authentication."""
        return auth_util.is_api_key_auth(request)

    def get_hashed_user_id(self, request: Request) -> str | None:
        """Get the hashed user ID from the request session."""
        return auth_util.get_hashed_user_id(request)

    def _add_rules_endpoints(self):
        @self.app.get("/api/rules")
        @logger.catch(reraise=True)
        def get_rules(
            request: Request,
            rule_id: str = Query(..., description="Rule ID to retrieve"),
        ):
            """
            Handle HTTP GET requests for retrieving a specific rule by its ID.

            This API endpoint allows the client to request a specific rule's content by providing
            a valid rule ID as a query parameter. The rule ID is validated to ensure that it meets
            the expected format. If the rule exists in the loaded set of rules, the content of the
            rule is returned as plain text. If the rule does not exist, an appropriate HTTP error
            message is returned. The endpoint also captures analytics for both successful and
            unsuccessful accesses.

            :param request: The incoming HTTP request object
            :type request: Request
            :param rule_id: Rule ID to retrieve, passed as a query parameter in the request
            :type rule_id: str
            :return: Plain text response containing the content of the requested rule if found,
                     otherwise an HTTP error message
            :rtype: PlainTextResponse or HTTPException

            :raises HTTPException: If the rule ID format is invalid, the rule is not found, or
                                   if there is a server error during processing
            """

            def is_valid_rule_id(value: str) -> bool:
                """Validate rule ID format."""
                return bool(value) and re.match(r"^[a-zA-Z0-9_-]{1,100}$", value)

            user_id = self.get_hashed_user_id(request)
            source = self._get_request_source(request)

            try:
                # Validate input parameter
                if not is_valid_rule_id(rule_id):
                    raise HTTPException(
                        status_code=400, detail="Invalid rule ID format"
                    )

                # Check if the requested rule exists in our loaded rules
                if rule_id in self.loaded_rules:
                    rule_data = self.loaded_rules[rule_id]

                    # Log successful rule access
                    HaivenLogger.get().analytics(
                        "Download rule",
                        {
                            "user_id": user_id,
                            "rule_id": rule_id,
                            "source": source,
                        },
                    )

                    return PlainTextResponse(
                        content=rule_data["content"], media_type="text/plain"
                    )
                else:
                    # Log failed rule access attempt
                    HaivenLogger.get().analytics(
                        "Download rule failed - not found",
                        {
                            "user_id": user_id,
                            "rule_id": rule_id,
                            "source": source,
                        },
                    )

                    # Provide a helpful error message with available rules
                    available_rules = list(self.loaded_rules.keys())
                    if available_rules:
                        error_msg = f"Rule '{rule_id}' not found. Available rules: {', '.join(available_rules)}"
                    else:
                        error_msg = f"Rule '{rule_id}' not found. No rules are currently loaded."

                    raise HTTPException(status_code=404, detail=error_msg)

            except HTTPException:
                raise
            except Exception as e:
                error_msg = str(e)
                HaivenLogger.get().error(
                    f"Error retrieving rule '{rule_id}': {error_msg}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Server error retrieving rule '{rule_id}': {error_msg}",
                )

        @self.app.get("/api/rules/list")
        @logger.catch(reraise=True)
        def list_rules():
            """
            Handles the API endpoint for listing all available rules. Generates a list of
            rules with details such as rule ID, filename, and metadata, and returns the
            list along with additional information about the loaded rules.

            Logs an error and raises an HTTPException in case of any internal processing
            errors.

            :return: A dictionary containing the list of rules, the total count of rules,
                     and a boolean indicating whether the rules are loaded
            :rtype: dict
            """

            try:
                rules_list = []
                for rule_id, rule_data in self.loaded_rules.items():
                    rules_list.append(
                        {
                            "id": rule_id,
                            "filename": rule_data["filename"],
                            "metadata": rule_data["metadata"],
                        }
                    )

                return {
                    "rules": rules_list,
                    "count": len(rules_list),
                    "loaded": self.rules_loaded,
                }

            except Exception as e:
                error_msg = str(e)
                HaivenLogger.get().error(f"Error listing rules: {error_msg}")
                raise HTTPException(
                    status_code=500, detail=f"Server error listing rules: {error_msg}"
                )
