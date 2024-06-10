# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch
from shared.services.agents_service import AgentsService


class TestAgentsService:
    @patch("boto3.client")
    @patch("shared.services.agents_service.ConfigService.load_enabled_providers")
    @patch("shared.services.agents_service.ConfigService.load_agent_info")
    def test_init(
        self, mock_load_agent_info, mock_load_enabled_providers, mock_boto3_client
    ):
        mock_load_enabled_providers.return_value = ["aws"]
        mock_load_agent_info.return_value = {
            "enabled_agent_ids": ["id1"],
            "enabled_agent_alias_ids": ["alias_id1"],
            "region_name": "us-west-2",
        }
        mock_boto3_client.return_value.get_agent.return_value = {
            "agent": {"description": "description", "agentName": "agentName"}
        }
        mock_boto3_client.return_value.get_agent_alias.return_value = {
            "agentAlias": {"agentAliasName": "agentAliasName"}
        }
        AgentsService.reset_instance()
        service = AgentsService.get_instance()
        assert service.get_agent_info() == [
            {
                "agentId": "id1",
                "agentName": "agentName",
                "agentAliasId": "alias_id1",
                "agentAliasName": "agentAliasName",
                "description": "description",
            }
        ]
        assert service.get_agent_region() == "us-west-2"

    @patch("boto3.client")
    @patch("shared.services.agents_service.ConfigService.load_enabled_providers")
    @patch("shared.services.agents_service.ConfigService.load_agent_info")
    def test_get_agent_response(
        self, mock_load_agent_info, mock_load_enabled_providers, mock_boto3_client
    ):
        mock_boto3_client.return_value.invoke_agent.return_value = {
            "completion": [
                {
                    "chunk": {
                        "bytes": b"ABCD",
                        "attribution": {
                            "citations": [
                                {
                                    "retrievedReferences": [
                                        {
                                            "content": {"text": "Test Text"},
                                            "location": {
                                                "s3Location": {"uri": "Source URI"},
                                                "type": "S3",
                                            },
                                        }
                                    ]
                                }
                            ]
                        },
                    }
                }
            ]
        }
        mock_load_enabled_providers.return_value = ["aws"]
        mock_load_agent_info.return_value = {
            "enabled_agent_ids": ["id1"],
            "enabled_agent_alias_ids": ["alias_id1"],
            "region_name": "us-west-2",
        }
        mock_boto3_client.return_value.get_agent.return_value = {
            "agent": {"description": "description", "agentName": "agentName"}
        }
        mock_boto3_client.return_value.get_agent_alias.return_value = {
            "agentAlias": {"agentAliasName": "agentAliasName"}
        }
        AgentsService.reset_instance()
        service = AgentsService.get_instance()
        response = service.get_agent_response("question", "agent_id", "agent_alias_id")
        assert response == ("ABCD", "- Test Text \nSource: `Source URI`")
