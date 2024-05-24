# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
class DefaultModels:
    def __init__(self, chat, vision, embeddings):
        self.chat = chat
        self.vision = vision
        self.embeddings = embeddings

    @classmethod
    def from_dict(cls, data):
        return cls(data.get("chat"), data.get("vision"), data.get("embeddings"))
