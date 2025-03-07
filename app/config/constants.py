# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
# Number of messages after which we should summarize the conversation
CONVERSATION_LENGTH_THRESHOLD = 4  # Adjust this value based on your needs

# Chat configuration
MAX_TOKENS = 2000
DISCLAIMER_PATH = "disclaimer/disclaimer_and_guidelines.md"
SYSTEM_MESSAGE = """You are Haiven, an assistant for teams who deliver software. You help with tasks related to agile software delivery.

- Be professional, concise, and actionable. When necessary, challenge assumptions or suggest alternatives, but do so constructively.
- If the user request includes instructions in a language other than English, ask them if you should switch to that language
- Provide your responses in markdown format, UNLESS OTHERWISE SPECIFIED."""
STANDALONE_QUESTION_SYSTEM_MESSAGE = "You are an expert at creating standalone questions that capture context from conversations."
