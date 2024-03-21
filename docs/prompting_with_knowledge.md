# Prompting with knowledge

## Requirement

As a user, I want to be able to pull in relevant team knowledge into my tasks and chat conversations. I don't want to have to think too much about what knowledge would be relevant, instead I want it to come up naturally depending on the task/chat context

## Solutions tried

### 1. Add a knowledge entry to the prompt

Implementation:

- Take the user's chat message and feed it to the similarity search
- Start the prompt with "consider this additional context. if you don't find anything relevant to my request in the context, ignore the context"
- Also tried, "at the end, give me some additional advice based on this context: ..."

Consequences:

- It seems to be hard to get the AI to also consider its own "world knowledge", and ignore the context when there is nothing in the context that is relevant to the request. 
- ?? What is the consequence of long prompt as the query for similarity search? Does that even work? Haven't found anything yet that explains it.

### 2. Offer the user buttons to say, "now include this knowledge base"

Implementation:

- Have a choice of knowledge below the chat message box, and let the user choose one
- On choosing one, have a model summarise the conversation so far, and do a similarity search based on that. 
- Use the search results and the summary (only?) to create a prompt for advice

Consequences:

- The user has to explicitly decide to include a context, instead of it being chosen automatically. On the other hand, this creates more control and less "magic" and unintended consequences