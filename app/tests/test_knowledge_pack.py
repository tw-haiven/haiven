# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch
from tests.utils import get_test_data_path
from shared.models.knowledge_pack import KnowledgePack


class TestKnowledgePack:
    test_knowledge_pack_path = get_test_data_path() + "/test_knowledge_pack"

    def test_auto_discovery_contexts_called_on_init(self):
        with patch.object(
            KnowledgePack, "_auto_discovery_contexts"
        ) as mock_auto_discovery:
            _ = KnowledgePack(self.test_knowledge_pack_path)
            mock_auto_discovery.assert_called_once()

    def test_auto_discovery_contexts(self):
        knowledge_pack = KnowledgePack(self.test_knowledge_pack_path)

        assert len(knowledge_pack.contexts) == 2

        # Create a dictionary to map context names to paths
        context_dict = {
            context.name: context.path for context in knowledge_pack.contexts
        }

        # Check that the contexts have the correct names and paths
        assert context_dict.get("context_a") == "context_a"
        assert context_dict.get("context_b") == "context_b"

    def test_auto_discovery_contexts_no_contexts_folder(self):
        knowledge_pack = KnowledgePack(
            self.test_knowledge_pack_path + "/contexts/context_b"
        )

        assert len(knowledge_pack.contexts) == 0
