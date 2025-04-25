# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import pytest
from knowledge.markdown import KnowledgeBaseMarkdown, KnowledgeMarkdown


def test_aggregate_context_contents():
    # Arrange
    kb = KnowledgeBaseMarkdown()
    kb._knowledge = {
        'context1': KnowledgeMarkdown('Content 1', {}),
        'context2': KnowledgeMarkdown('Content 2', {}),
        'context3': KnowledgeMarkdown('Content 3', {})
    }
    
    user_context = "user's context"
    # Act
    result = kb.aggregate_all_contexts(['context1', 'context2', 'context3'], user_context)
    # Assert
    assert result == 'Content 1\n\nContent 2\n\nContent 3\n\nuser\'s context'


def test_aggregate_context_if_both_contexts_and_user_context_is_None():
    # Arrange
    kb = KnowledgeBaseMarkdown()
    kb._knowledge = {
        'context1': KnowledgeMarkdown('Content 1', {}),
        'context2': KnowledgeMarkdown('Content 2', {})
    }
    
    # Act
    result = kb.aggregate_all_contexts(None)
    
    # Assert
    assert result == ''


def test_aggregate_context_contents_single_context():
    # Arrange
    kb = KnowledgeBaseMarkdown()
    kb._knowledge = {
        'context1': KnowledgeMarkdown('Content 1', {}),
        'context2': KnowledgeMarkdown('Content 2', {})
    }
    
    # Act
    result = kb.aggregate_all_contexts(['context1'])
    
    # Assert
    assert result == 'Content 1'


def test_aggregate_context_contents_invalid_key():
    # Arrange
    kb = KnowledgeBaseMarkdown()
    kb._knowledge = {
        'context1': KnowledgeMarkdown('Content 1', {}),
        'context2': KnowledgeMarkdown('Content 2', {})
    }
    
    # Act & Assert
    with pytest.raises(KeyError):
        kb.aggregate_all_contexts(['invalid_key'])

def test_aggregate_context_if_only_user_context_is_provided():
    kb = KnowledgeBaseMarkdown()
    kb._knowledge = {
        'context1': KnowledgeMarkdown('Content 1', {}),
        'context2': KnowledgeMarkdown('Content 2', {})
    }
    
    result = kb.aggregate_all_contexts([], "user's context")

    assert result == "user's context"
    