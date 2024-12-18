# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import frontmatter
import json
import os
from config.constants import DISCLAIMER_PATH


class WelcomeMessageService:
    def __init__(self, knowledge_pack_path: str):
        self.knowledge_pack_path = knowledge_pack_path
        self.is_enabled = self._check_welcome_message_exists()
        self.welcome_message_json = (
            self.fetch_welcome_message() if self.is_enabled else None
        )

    def _check_welcome_message_exists(self):
        md_file_path = f"{self.knowledge_pack_path}/{DISCLAIMER_PATH}"
        return os.path.exists(md_file_path)

    def fetch_welcome_message(self):
        if not self.is_enabled:
            return json.dumps({"title": "", "content": ""})

        md_file_path = f"{self.knowledge_pack_path}/{DISCLAIMER_PATH}"
        with open(md_file_path, "r") as file:
            post = frontmatter.load(file)

        title = post.get("title", "No Title")
        content = post.content
        message_data = {"title": title, "content": content}

        return json.dumps(message_data, indent=4)
