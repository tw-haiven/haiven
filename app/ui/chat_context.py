# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ChatContext:
    tab_id: str
    interaction_pattern: str
    model: str
    temperature: float
    prompt: str
    message: str
