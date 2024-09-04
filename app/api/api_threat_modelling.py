# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from api.models.explore_request import ExploreRequest
from api.api_basics import HaivenBaseApi


def get_explore_kickoff_prompt(originalInput, item, user_message):
    return f"""
    You are a member of a software engineering team and are assisting me in threat modeling.
    
    You will help me to identify and analyze potential security threats and vulnerabilities within 
    the following APPLICATION:
    
    {originalInput}

    I want to work with you on the following THREAT SCENARIO in that context:
    {item}
    
    To kick us off, I have the following request for you, please help me:
    {user_message}

    Based on your inputs, I will guide you through the process of exploring this 
    threat scenario. I will help generate questions and considerations that may 
    expose potential risks and suggest security measures that could be implemented 
    to mitigate these risks. Our goal is to ensure a thorough understanding and 
    preparation against possible security threats facing your project.
    """


class ApiThreatModelling(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.post("/api/threat-modelling/explore")
        def chat(explore_request: ExploreRequest):
            prompt = explore_request.userMessage
            if explore_request.chatSessionId is None:
                prompt = get_explore_kickoff_prompt(
                    explore_request.originalInput,
                    explore_request.item,
                    explore_request.userMessage,
                )

            return self.stream_text_chat(
                prompt, "threat-modelling-explore", explore_request.chatSessionId
            )
