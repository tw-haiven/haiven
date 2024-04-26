# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import patch
from shared.models.knowledge_pack import KnowledgePack


class TestKnowledgePack:
    test_knowledge_pack_path = "tests/test_data/test_knowledge_pack"

    def test_auto_discovery_contexts_called_on_init(self):
        with patch.object(
            KnowledgePack, "_auto_discovery_contexts"
        ) as mock_auto_discovery:
            _ = KnowledgePack(self.test_knowledge_pack_path)
            mock_auto_discovery.assert_called_once()

    def test_auto_discovery_contexts(self):
        knowledge_pack = KnowledgePack(self.test_knowledge_pack_path)

        assert len(knowledge_pack.contexts) == 2
        assert knowledge_pack.contexts[0].name == "context_a"
        assert knowledge_pack.contexts[0].path == "context_a"
        assert knowledge_pack.contexts[1].name == "context_b"
        assert knowledge_pack.contexts[1].path == "context_b"

    def test_auto_discovery_contexts_no_contexts_folder(self):
        knowledge_pack = KnowledgePack(
            self.test_knowledge_pack_path + "/contexts/context_b"
        )

        assert len(knowledge_pack.contexts) == 0
