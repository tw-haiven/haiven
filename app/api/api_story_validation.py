# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi
from fastapi import Request


class QuestionAnswer(BaseModel):
    # In parallel we're building the new reusable follow-up functionality, need to use the new generic property names for compatibility
    title: str = None  # question
    summary: str = None  # answer
    thought: str = None


class StoryValidationScenarios(BaseModel):
    input: str = None
    answers: List[QuestionAnswer] = []
    promptIdForLogging: str = None


def _concat_questions_answers(validationScenarios: StoryValidationScenarios):
    return [
        f"**Your question:** {qa.title}\n**My REVISED ANSWER:** {qa.summary}"
        for qa in validationScenarios.answers
    ]


def get_invest_critique_prompt(validationScenarios: StoryValidationScenarios):
    return f"""

    You are an analyst on a software engineering team.

# TASK
Create a summary of my requirements, then critique if they are a good scope for a user story by applying the "INVEST" criteria. 
We want to have as small a work package / user story as possible, but at the same time we need to make sure that it is big enough that it makes sense and creates value for the user.

# CONTEXT
Here is my input that describes my application and requirements:

{validationScenarios.input}
    
    A developer asked me a bunch of questions about this story, here are the questions and the answers I gave them:

{_concat_questions_answers(validationScenarios)}

# INSTRUCTIONS

1. Summarise my requirements

2. Think about each of the INVEST criteria and whether the scope of my requirements fulfills each criterion (yes/no), and the reasons why you think they do or does not.
The INVEST criteria are:
- Independent: Can the story be completed independently of others?
- Negotiable: Is the story flexible and open to changes?
- Valuable: Does it deliver clear value?
- Estimable: Can you estimate it with a reasonable degree of certainty?
- Small: Is it small enough to complete within a sprint?
- Testable: Can it be validated easily?

When you give me your critique, group the criteria by the ones you consider as "yes", and the ones you consider a "no".

3. Think about the following questions. If you think that any of them are worth for me to think about further to make the story either smaller or more comprehensive, to improve the scope and thin slicing of the story, then mention it to me, and tell me why you think I should consider it.
- Are there any variations or exceptions that we could treat as independent work packages and pull out into another story?
- Can we split this into two or more steps to keep progress smooth?
- What is the most important thing to deliver now that will help validate assumptions? Can we limit the story to only that?
- Are we really only using the simplest way to achieve the core goal of this requirement?
- Can this user story stand alone and offer value to the user?
- Does this slice cross all layers and deliver end-to-end value?

Return the results of all 3 steps to me. Use markdown format for better readability.

    """


def get_summary_prompt(validationScenarios: StoryValidationScenarios):
    return f"""

    You are an analyst on a software engineering team.

# TASK
Help me draft a user story summary

# CONTEXT
Here is my input that describes my application and user story:

{validationScenarios.input}
    
    A developer asked me a bunch of questions about this story, here are the questions and the answers I gave them:

{_concat_questions_answers(validationScenarios)}

# INSTRUCTIONS
Based on my original input, and the questions and answers, come up with a list of requirements for this story. 
The list should be a concise summary of the general requirements. The developers on the team are quite experienced and do not need detailed
acceptance criteria, I just want to give them a list of the things needed to implement this story, as a placeholder for our conversation.

    """


def get_given_when_then_generation_prompt(
    validationScenarios: StoryValidationScenarios,
):
    return f"""

    You are an analyst on a software engineering team.

# TASK
Help me draft a user story with Given/When/Then scenarios

# CONTEXT
Here is my input that describes my application and user story:

{validationScenarios.input}
    
    A developer asked me a bunch of questions about this story, here are the questions and the answers I gave them:

{_concat_questions_answers(validationScenarios)}

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

        @app.post("/api/story-validation/summary")
        def generate_summary(request: Request, body: StoryValidationScenarios):
            origin_url = request.headers.get("referer")
            prompt = get_summary_prompt(body)

            return self.stream_text_chat(
                prompt=prompt,
                chat_category="story-validation-summary",
                user_identifier=self.get_hashed_user_id(request),
                origin_url=origin_url,
                prompt_id_for_logging=body.promptIdForLogging,
            )

        @app.post("/api/story-validation/scenarios")
        def generate_scenarios(request: Request, body: StoryValidationScenarios):
            origin_url = request.headers.get("referer")
            prompt = get_given_when_then_generation_prompt(body)

            return self.stream_text_chat(
                prompt=prompt,
                chat_category="story-validation-scenarios",
                user_identifier=self.get_hashed_user_id(request),
                origin_url=origin_url,
                prompt_id_for_logging=body.promptIdForLogging,
            )

        @app.post("/api/story-validation/invest")
        def generate_invest_critique(request: Request, body: StoryValidationScenarios):
            origin_url = request.headers.get("referer")
            prompt = get_invest_critique_prompt(body)

            return self.stream_text_chat(
                prompt=prompt,
                chat_category="story-validation-invest",
                user_identifier=self.get_hashed_user_id(request),
                origin_url=origin_url,
                prompt_id_for_logging=body.promptIdForLogging,
            )
