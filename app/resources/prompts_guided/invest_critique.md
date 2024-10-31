---
identifier: guided-invest-critique-983b8b
title: "INVEST Critique"
system: "You are an analyst on a software engineering team."
categories: ["guided"]

help_prompt_description: "Generate a critique of the size of these requirements, and their suitability for a thinly sliced user story."
---
You are an analyst on a software engineering team.

# TASK
Create a summary of my requirements, then critique if they are a good scope for a user story by applying the "INVEST" criteria. 
We want to have as small a work package / user story as possible, but at the same time we need to make sure that it is big enough that it makes sense and creates value for the user.

# CONTEXT
Here is my input that describes my application and requirements:

{user_input}

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
