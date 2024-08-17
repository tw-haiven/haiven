# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi


class StoryValidationQuestions(BaseModel):
    input: str


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class StoryValidationScenarios(BaseModel):
    input: str
    answers: List[QuestionAnswer]


def get_story_generation_prompt(validationScenarios: StoryValidationScenarios):
    refined_input = [
        f"**Your question:** {qa.question}\n**My REVISED ANSWER:** {qa.answer}"
        for qa in validationScenarios.answers
    ]

    return f"""

    You are an analyst on a software engineering team.

# TASK
Help me draft a user story with Given/When/Then scenarios

# CONTEXT
Here is my input that describes my application and user story:

{validationScenarios.input}
    
    A developer asked me a bunch of questions about this story, here are the questions and the answers I gave them:

{refined_input}

# INSTRUCTIONS
Based on my original input, and the questions and answers, come up with given/when/then scenarios for the user story.

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


class ApiStoryValidation(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.post("/api/story-validation/questions")
        def story_validation(body: StoryValidationQuestions):
            prompt = prompt_list.render_prompt(
                active_knowledge_context=None,
                prompt_choice="guided-story-validation",
                user_input=body.input,
                additional_vars={},
                warnings=[],
            )

            return self.stream_json_chat(prompt, "story-validation")

        @app.post("/api/story-validation/scenarios")
        def generate_scenarios(body: StoryValidationScenarios):
            prompt = get_story_generation_prompt(body)

            return self.stream_text_chat(prompt, "story-validation-generate")
