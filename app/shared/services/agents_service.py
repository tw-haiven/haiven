# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from shared.services.config_service import ConfigService
import boto3
import re
import uuid
from shared.logger import HaivenLogger


class AgentsService:
    __instance = None

    def __init__(self, config_path: str = "config.yaml"):
        self.__agent_data = None
        self.__agent_region = None
        if AgentsService.__instance is not None:
            raise Exception(
                "AgentsService is a singleton class. Use get_instance() to get the instance."
            )
        AgentsService.__instance = self

        enabled_providers = ConfigService.load_enabled_providers()
        if "aws" not in enabled_providers:
            return

        enabled_agent_config = ConfigService.load_agent_info()
        if not enabled_agent_config:
            return

        agent_ids = enabled_agent_config["enabled_agent_ids"]
        agent_alias_ids = enabled_agent_config["enabled_agent_alias_ids"]
        if not agent_ids or not agent_alias_ids:
            return

        if not isinstance(agent_ids, list):
            agent_ids = [agent_ids]
        if not isinstance(agent_alias_ids, list):
            agent_alias_ids = [agent_alias_ids]

        if len(agent_ids) != len(agent_alias_ids):
            HaivenLogger.get().logger.error("Mismatch of agentIds and agentAliasIds")
            raise ValueError("Mismatch of agentIds and agentAliasIds")

        region = enabled_agent_config["region_name"]
        if not region:
            return
        else:
            self.__agent_region = region

        agent_client = boto3.client("bedrock-agent", region_name=region)
        agent_data = []
        for agent_id, agent_alias_id in zip(agent_ids, agent_alias_ids):
            try:
                agent_info = agent_client.get_agent(agentId=agent_id)
                agent_description = agent_info["agent"]["description"]
                agent_name = agent_info["agent"]["agentName"]
                agent_alias = agent_client.get_agent_alias(
                    agentAliasId=agent_alias_id, agentId=agent_id
                )
                agent_alias_name = agent_alias["agentAlias"]["agentAliasName"]
                agent_data.append(
                    {
                        "agentId": agent_id,
                        "agentName": agent_name,
                        "agentAliasId": agent_alias_id,
                        "agentAliasName": agent_alias_name,
                        "description": agent_description,
                    }
                )
            except Exception as e:
                HaivenLogger.get().logger.warning("Error loading agent information!!")
                HaivenLogger.get().logger.info(e)

        if len(agent_data) > 0:
            self.__agent_data = agent_data

    @staticmethod
    def get_agent_info():
        return AgentsService.get_instance().__agent_data

    @staticmethod
    def get_agent_region():
        return AgentsService.get_instance().__agent_region

    @staticmethod
    def get_instance():
        if AgentsService.__instance is None:
            AgentsService()

        return AgentsService.__instance

    @staticmethod
    def reset_instance():
        AgentsService.__instance = None

    @staticmethod
    def __remove_square_brackets(text):
        return re.sub(r"\[\d+\]", "", text)

    @staticmethod
    def __list_references(attribution):
        references = []
        for citation in attribution["citations"]:
            for reference in citation["retrievedReferences"]:
                text = AgentsService.__remove_square_brackets(
                    reference["content"]["text"]
                )
                reference_text = text[:100] + (text[100:] and "...")
                reference_url = reference["location"]["s3Location"]["uri"]
                reference_md = f"- {reference_text} \nSource: `{reference_url}`"
                references.append(reference_md)
        return "\n".join(references)

    @staticmethod
    def get_agent_response(question: str, agent_id: str, agent_alias_id: str):
        agent_runtime = boto3.client(
            "bedrock-agent-runtime", region_name=AgentsService.get_agent_region()
        )
        agent_response = agent_runtime.invoke_agent(
            agentId=agent_id,
            inputText=question,
            agentAliasId=agent_alias_id,
            sessionId=str(uuid.uuid4()),
        )
        completion = ""
        attributions = ""
        for event in agent_response.get("completion"):
            chunk = event["chunk"]
            completion = completion + chunk["bytes"].decode()
            if "attribution" in chunk:
                attributions = attributions + AgentsService.__list_references(
                    chunk["attribution"]
                )
        return completion, attributions
