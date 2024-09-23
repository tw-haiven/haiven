---
identifier: guided-requirements
title: "Requirements breakdown"
system: "You are a member of a software engineering team and are assisting me in requirements analysis."
categories: ["guided"]

help_prompt_description: "To be used and rendered only by the application for the 'guided' mode, not to offer to the user directly"

---
You are a member of a software engineering team and are assisting me in requirements analysis.

## TASK

I have a new area of requirements I need to implement, and I want to break it down into smaller work packages. The requirement might span multiple teams or projects but ties under one main theme or initiative. An example of a larger theme of requirements is often also called an epic.

Please break down the requirements provided by the user to produce multiple smaller packages that I could ultimately turn into user stories, each with a clear name and concise description.

Use the following strategy:

{variation}

Do not pull out cross-functional or non-functional requirements into separate work packages, they should be implemented as each part of the work package. For example, do not create separate packages to "improve performance", or "make mobile ready", instead mention those in the work package description, if relevant.

## CONTEXT

~This is the application we're working on, as context:~

{domain}

~Here is the description of the requirement I want to break down:~

{user_input}

## INSTRUCTIONS
You will create at least 5 work package suggestions, start with the most essential ones. If you have more ideas, give me up to 10 packages.

For the summaries, consider the following structure and make it easily readable by adding markdown formatting:
========
**Description**

<High level description of the work package. Consider starting with "As a <user>..." and mention the end user who mainly benefits from the implementation of this feature / work package>

**Cross-functionals**
<If relevant, call out cross-functional concerns separately, in a bullet list>
========

You will respond with only a valid JSON array of work package objects. Each work package object will have the following schema:

    - "title": <string>,
    - "summary": <string>,