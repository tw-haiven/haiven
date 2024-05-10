# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from fastapi import Request
from fastapi.responses import StreamingResponse
from shared.chats import JSONChat
from shared.llm_config import LLMConfig


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

Come up with 2-3 questions that you would ask to clarify the user story:
- Thought: Think about what is still uncertain about defining the user story. Ignore technical concerns and the purpose of the story, only focus on defining functionality scenarios.
- Question: a question to ask to clarify the user story
- The answer you suggest for the question

You will respond with only a valid JSON array of question-answer objects. Each object will have the following schema:
    "thought": <string>,
    "question": <string>,
    "answer": <string>,

    """


# at least 5, at most 10 thought/question/answer groups:
def enable_story_validation(app, chat_session_memory):
    @app.get("/api/story-validation")
    def story_validation(request: Request):
        input = request.query_params.get("input")

        chat_session_key_value, chat_session = chat_session_memory.get_or_create_chat(
            lambda: JSONChat(llm_config=LLMConfig("azure-gpt4", 0.5)),
            None,
            "story-validation",
            # TODO: Pass user identifier from session
        )

        return StreamingResponse(
            chat_session.run(get_story_validation_prompt(input)),
            media_type="text/event-stream",
            headers={
                "Connection": "keep-alive",
                "Content-Encoding": "none",
                "Access-Control-Expose-Headers": "X-Chat-ID",
                "X-Chat-ID": chat_session_key_value,
            },
        )

    # def generate_scenarios(request: Request):
    #     input = request.query_params.get("input")

    #     json_chat = JSONChat()  # LLMConfig("mock", 0.5))
    #     return StreamingResponse(
    #         json_chat.run(get_story_validation_prompt(input)),
    #         media_type="text/event-stream",
    #         headers={
    #             "Connection": "keep-alive",
    #             "Content-Encoding": "none",  # Necessary for the stream to work across the Next rewrite
    #         },
    #     )
