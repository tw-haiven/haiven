# Differences in the models

## Brainstorming

Our "Brainstorming" interaction pattern uses a "Thought/Question/Answer" ReAct prompting sequence to allow the model to ask questions to the user. It uses a stop sequence in the API call to get the model to stop when they get to "Answer:" (because we want the user to answer the question, not the model)

### GPTs

This works best (and only?) with the GPT models, at least with the prompt that we currently have.

### Claude v2

Claude just keeps asking the same question. You can nudge it to ask another one, manually, but then it still stops after 2 questions, a lot shorter than what the GPTs are doing

### Llama 2

I did kind of get it to work on the AWS playground with this prompt:

```plaintext
[INST]You are a a very intelligent bot with exceptional critical thinking[/INST]

You're part of a team building a web application that will allow salespeople in a company to organise their work and document their customer relationships. Help me think through a user story an generate acceptence criteria scenarios.

USER STORY:
Plan activity for a specific date: The sales manager user should be able to add a new planned activity to the application, for a specific customer, with a date and some notes describing what they want to do

Use the following thought process:

Thought: think about what is still unknown about defining the user story. 
Question: the question to ask to clarify the user story
Answer: the answer to the question

(repeat this Thought/Question/Answer repeat at least 3 times)  

Thought: I know enough to explain the user story
Scenarios: List all possible scenarios with concrete example in Given/When/Then style

Start to think Thought by Thought
```

> Note: using metatags like [INST] seems to be a thing with open source models that can significantly improve the performance, I took this one from one of the chain-of-thought examples on the Bedrock playground

> BUT: Llama API does not support stop sequences?!
