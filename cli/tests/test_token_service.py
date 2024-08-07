# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from haiven_cli.services.token_service import TokenService
from unittest.mock import MagicMock, patch


class TestTokenService:
    @patch("haiven_cli.services.token_service.tiktoken")
    def test_get_tokens_length(self, mock_tiktoken):
        tokens = [1, 1, 1]
        tokenizer = MagicMock()
        tokenizer.encode.return_value = tokens
        mock_tiktoken.get_encoding.return_value = tokenizer

        encoding = "cl100k_base"
        token_service = TokenService(encoding)

        text_splitter = MagicMock()
        tokens_length = token_service.get_tokens_length(text_splitter)

        mock_tiktoken.get_encoding.assert_called_with(encoding)
        tokenizer.encode.assert_called_with(text_splitter, disallowed_special=())
        assert tokens_length == len(tokens)
