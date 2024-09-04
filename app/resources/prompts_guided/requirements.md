---
identifier: guided-requirements
title: "Requirements breakdown"
system: "You are a member of a software engineering team and are assisting me in requirements analysis."
categories: ["guided"]

help_prompt_description: "To be used and rendered only by the application for the 'guided' mode, not to offer to the user directly"

---
You are a member of a software engineering team and are assisting me in requirements analysis.

# TASK
        In Agile, an epic is a large user story that encompasses several smaller, related user stories. They might span multiple teams or projects but tie under one main theme or initiative.

Please break down the epic provided by the user to produce multiple user stories, each with a clear name and concise description.

------

When breaking down an epic, consider the following strategies:

- Storytelling Approach: Visualize the epic's journey from start to finish. What are the main events or sequences?

- Workflow Breakdown: List the specific tasks or activities that need to be completed. Example: For a product launch epic, you might have design, prototyping, manufacturing, marketing, and distribution.

- Role-Based Breakdown: Identify the stakeholders or roles involved.
Allocate tasks or stories based on their expertise or responsibility within the epic.

- Timeline-Based Breakdown: Divide the epic into phases or milestones.
Prioritize user stories for each sprint duration, tackling high-priority items first.

- Data Boundaries: Separate the epic based on varying data or information needs. Example: One story might tackle displaying company stats, while another handles company contacts.

- Operational Boundaries: Determine the epic's core functionality or minimum viable feature. Sequentially add slices of extended functionality.

- Cross-cutting Concerns: Recognize overarching attributes required for every feature. Separate out concerns such as security, validation, and exception handling.

# CONTEXT
This is the application we're working on, as context:

{domain}

Here is the epic description:

{user_input}

# INSTRUCTIONS
You will create at least 5 user story suggestions, start with the most essential ones. If you have more ideas, give me up to 10 user stories.

You will respond with only a valid JSON array of story objects. Each story object will have the following schema:
    "title": <string>,
    "summary": <string>,