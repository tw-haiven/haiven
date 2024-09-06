# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
class HaivenUrl:
    def __init__(self):
        self.PATH_ABOUT = "about"
        self.PATH_ANALYSIS = "analysis"
        self.PATH_AUTH = "auth"
        self.PATH_CHAT = "chat"
        self.PATH_CODING = "coding"
        self.PATH_GENERAL_DEPRECATED = "teamai"  # Supported for people with old links
        self.PATH_KNOWLEDGE = "knowledge"
        self.PATH_LOGIN = "login"
        self.PATH_LOGOUT = "logout"
        self.PATH_TESTING = "testing"
        self.PATH_BOBA = "boba"

    def about(self):
        return f"/{self.PATH_ABOUT}"

    def analysis(self):
        return f"/{self.PATH_ANALYSIS}"

    def auth(self):
        return f"/{self.PATH_AUTH}"

    def chat(self):
        return f"/{self.PATH_CHAT}"

    def coding(self):
        return f"/{self.PATH_CODING}"

    def general(self):
        return f"/{self.PATH_GENERAL_DEPRECATED}"

    def knowledge(self):
        return f"/{self.PATH_KNOWLEDGE}"

    def login(self):
        return f"/{self.PATH_LOGIN}"

    def logout(self):
        return f"/{self.PATH_LOGOUT}"

    def testing(self):
        return f"/{self.PATH_TESTING}"

    def boba(self):
        return f"/{self.PATH_BOBA}"
