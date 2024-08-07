# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import tiktoken


class TokenService:
    def __init__(self, encoding: str = "cl100k_base"):
        self.encoding = encoding

    def get_tokens_length(self, s) -> int:
        tokenizer = tiktoken.get_encoding(self.encoding)
        tokens = tokenizer.encode(s, disallowed_special=())
        return len(tokens)
