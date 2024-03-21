# ADR 1: Own implementation of LLM integration with only minimal use of Langchain

## Context

Our requirements:

- We need a library to call large language model APIs
- At the moment, we want to be able to call a range of different LLM services
- We mainly need simple chat conversations
- The one more advanced chat we have is a "Q&A" where the AI asks us questions. This requires the use of stop sequences, and of parsing the output of the model to extract the question.

Options:

1. The most commonly used option out there at the moment is LangChain. However, it is quite complex, and we experienced many of the things mentioned in this [article](https://minimaxir.com/2023/07/langchain-problem/). For example, it obfuscates a lot of what is actually going on, which makes it harder to learn how LLM integration works. It also feels very overengineered and hard to understand from a library user point of view. And it was not trivial to figure out how to make it stream responses. 
2. Use one of the other libraries out there that do similar things, e.g. Llamaindex, Haystack, Semantic Kernel
3. Implement ourselves, with the SDKs that come from the model services (e.g. OpenAI's SDK, or Amazon's for Bedrock, or Google's for Vertex, etc)
4. Implement ourselves, with a little bit of utility from LangChain to more easily cover the range of model services

## Decision

Option 4. -> Use LangChain for some of the basics, but as long as we do not need more advanced functionality that is not easy to implement ourselves, avoid it.

What we are still using it for:

- As a facade to use multiple different models with the same API (`BaseChatModel`, `HumanMessage`, `SystemMessage`, `AIMessage`)
- For prompt templates (although those would probably be super easy to replace with e.g. Jinja2, which is in our dependencies anyway)

## Consequences

- The original codebase used LangChain, but we have since stripped it down to the basics and implemented the rest ourselves (which reduced the codebase at the time by ~200 lines of code).
- It is now much more explicit and readable what's actually going on in the code, and what functionality we currently need and do not need.

Trade-offs:

- We might run into situations in the future where we do need advanced capabilities that we do not want to build ourselves. Then we can look at LangChain again, should we not find this functionality somewhere else.
- Because we are still using LangChain for some basic functionality, this might make it more tempting to use it for other things as well in the future, because it is convenient. It would be even better to remove LangChain altogether as long as we do not need it, but it was convenient to keep for a few things.
