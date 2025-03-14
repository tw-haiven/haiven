# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch
from tests.utils import get_test_data_path
from knowledge.pack import KnowledgePack


class TestKnowledgePack:
    test_knowledge_pack_path = get_test_data_path() + "/test_knowledge_pack"

    def test_auto_discovery_contexts_called_on_init(self):
        with patch.object(
            KnowledgePack, "_auto_discovery_contexts"
        ) as mock_auto_discovery:
            _ = KnowledgePack(get_test_data_path() + "/test_knowledge_pack")
            mock_auto_discovery.assert_called_once()

    def test_auto_discovery_contexts(self):
        knowledge_pack = KnowledgePack(get_test_data_path() + "/test_knowledge_pack")

        assert len(knowledge_pack.contexts) == 2

        context_dict = {
            context.name: {
                "name": context.name,
                "path": context.path,
                "title": context.title,
            }
            for context in knowledge_pack.contexts
        }

        # Check that the contexts have the correct names and paths
        assert context_dict.get("context_a").get("name") == "context_a"
        assert context_dict.get("context_b").get("name") == "context_b"

    def test_auto_discovery_contexts_no_contexts_folder(self):
        knowledge_pack = KnowledgePack(
            self.test_knowledge_pack_path + "/contexts/context_c"
        )

        assert len(knowledge_pack.contexts) == 0
