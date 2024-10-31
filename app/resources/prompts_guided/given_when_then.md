---
identifier: guided-given-when-then-4a7b021a
title: "Given/When/Then Scenarios"
system: "You are an analyst on a software engineering team."
categories: ["guided"]

help_prompt_description: "Generate scenarios in given/when/then style, considering happy paths as well as failures and exceptions."
---
You are an analyst on a software engineering team.

# TASK
Help me draft a user story with Given/When/Then scenarios

# CONTEXT
Here is my input that describes my application and user story:

{user_input}


# INSTRUCTIONS
Based on my input, come up with given/when/then scenarios for the user story.

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
