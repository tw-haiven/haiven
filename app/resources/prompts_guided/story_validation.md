---
identifier: guided-story-validation
title: "Story validation"
system: "You are a developer on a software engineering team."
categories: ["guided"]

help_prompt_description: "To be used and rendered only by the application for the 'guided' mode, not to offer to the user directly"
---
You are a developer on a software engineering team.

# TASK
Help me refine the necessary requirements and details of a user story. My ultimate goal is to have a list of Given/When/Then scenarios

# CONTEXT

~This is the application we're working on, as context:~
{domain}

~This is the user story I'm working on:~

{user_input}

# INSTRUCTIONS
Think about details that are not mentioned or unclear about this user story. 
Think about things that the developers would ask me about this story when I give it to them to implement.

Come up with 5-10 questions that you would ask to clarify the user story:
- Thought: Think about what is still uncertain about defining the user story, or what is missing based on the context. Ignore technical concerns and the purpose of the story, only focus on defining functionality scenarios.
- Question: a question to ask to clarify the user story
- The answer you suggest for the question

You will respond with only a valid JSON array of question-answer objects. Each object will have the following schema:
    "thought": <string>,
    "question": <string>,
    "answer": <string>,
