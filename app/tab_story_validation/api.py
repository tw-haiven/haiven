# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from shared.services.config_service import ConfigService
from shared.chats import JSONChat, ServerChatSessionMemory, StreamingChat
from shared.llm_config import LLMConfig


class StoryValidationQuestions(BaseModel):
    input: str


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class StoryValidationScenarios(BaseModel):
    input: str
    answers: List[QuestionAnswer]
    chat_session_id: str


def get_story_validation_prompt(input):
    return f"""
You are a member of a software engineering team.

# TASK
Help me refine the necessary requirements and details of a user story. My ultimate goal is to have a list of Given/When/Then scenarios

# CONTEXT
Here is my input that describes my application and user story:

{input}

# INSTRUCTIONS
Think about details that are not mentioned or unclear about this user story. 
Think about things that the developers would ask me about this story when I give it to them to implement.

Come up with 5-10 questions that you would ask to clarify the user story:
- Thought: Think about what is still uncertain about defining the user story. Ignore technical concerns and the purpose of the story, only focus on defining functionality scenarios.
- Question: a question to ask to clarify the user story
- The answer you suggest for the question

You will respond with only a valid JSON array of question-answer objects. Each object will have the following schema:
    "thought": <string>,
    "question": <string>,
    "answer": <string>,

    """


def get_scenario_generation_prompt(validationScenarios: StoryValidationScenarios):
    refined_input = [
        f"**Your question:** {qa.question}\n**My REVISED ANSWER:** {qa.answer}"
        for qa in validationScenarios.answers
    ]

    return f"""
I refined the answers to the questions you gave me:

{refined_input}

# INSTRUCTIONS
Based on my original input, and my REVISED ANSWERS, come up with given/when/then scenarios for the user story.

Use the following format:

    ## Happy paths
    **GIVEN** <preparation step to set up the test> 
    **WHEN** <action taken by a user, or some other event occurring>
    **THEN** <expected result>
    ## Sad paths
    ... (repeat the above format for each sad path)
    ## Exceptional paths
    ... (repeat the above format for each exceptional path)

An example from a different domain:
    ## Happy paths
    **GIVEN** a user is logged in
    **AND** they are on the Hotel search page
    **WHEN** they search for Hotels in a specific location and at a specific time
    **THEN** a list of all available Hotels associated with that location is displayed based on their price in ascending order

First think about the "happy paths", that is the basic scenarios that happen when everything goes well.
Then think about the "sad paths", that is the scenarios that happen when something goes wrong.
Then think about additional exceptional scenarios that are not covered by the happy or sad paths.

Respond with the given/when/then scenarios in Markdown format, putting each part of the scenario in a new line.

    """


# at least 5, at most 10 thought/question/answer groups:
def enable_story_validation(app, chat_session_memory: ServerChatSessionMemory):
    chat_model = ConfigService.get_default_guided_mode_model()

    @app.post("/api/story-validation/questions")
    def story_validation(body: StoryValidationQuestions):
        chat_session_key_value, chat_session = chat_session_memory.get_or_create_chat(
            lambda: JSONChat(
                llm_config=LLMConfig(chat_model, 0.5), event_stream_standard=False
            ),
            None,
            "story-validation",
            # TODO: Pass user identifier from session
        )

        return StreamingResponse(
            chat_session.run(get_story_validation_prompt(body.input)),
            media_type="text/event-stream",
            headers={
                "Connection": "keep-alive",
                "Content-Encoding": "none",
                "Access-Control-Expose-Headers": "X-Chat-ID",
                "X-Chat-ID": chat_session_key_value,
            },
        )

    @app.post("/api/story-validation/scenarios")
    def generate_scenarios(body: StoryValidationScenarios):
        chat_session_key_value, json_chat_session = (
            chat_session_memory.get_or_create_chat(
                None,
                body.chat_session_id,
                "story-validation",
                # TODO: Pass user identifier from session
            )
        )
        new_chat = StreamingChat(
            llm_config=LLMConfig(chat_model, 0.5), stream_in_chunks=True
        )
        new_chat.memory = json_chat_session.memory

        return StreamingResponse(
            new_chat.next(get_scenario_generation_prompt(body), []),
            media_type="text/event-stream",
            headers={
                "Connection": "keep-alive",
                "Content-Encoding": "none",
                "Access-Control-Expose-Headers": "X-Chat-ID",
                "X-Chat-ID": chat_session_key_value,
            },
        )
