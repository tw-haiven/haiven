# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json


class EventType(str, Enum):
    """Enumeration of all possible chat event types"""

    CONTENT = "content"
    METADATA = "metadata"
    TOKEN_USAGE = "token_usage"
    ERROR = "error"


class ChatEvent(BaseModel):
    """Base class for all chat events"""

    event_type: EventType = Field(..., description="Type of the event")

    def to_sse_format(self) -> str:
        """Convert event to Server-Sent Events format"""
        raise NotImplementedError("Subclasses must implement to_sse_format")


class ContentEvent(ChatEvent):
    """Event for streaming content chunks"""

    event_type: EventType = Field(
        default=EventType.CONTENT, description="Content event type"
    )
    content: str = Field(..., description="The content chunk to stream")

    def to_sse_format(self) -> str:
        """Convert to SSE format for streaming"""
        return f"data: {self.content}\n\n"


class MetadataEvent(ChatEvent):
    """Event for metadata with citations and other information"""

    event_type: EventType = Field(
        default=EventType.METADATA, description="Metadata event type"
    )
    citations: Optional[List[str]] = Field(
        default=None, description="List of citation URLs"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )

    def to_sse_format(self) -> str:
        """Convert to SSE format for streaming"""
        return f"data: {self.model_dump_json()}\n\n"


class TokenUsageEvent(ChatEvent):
    """Event for token usage information"""

    event_type: EventType = Field(
        default=EventType.TOKEN_USAGE, description="Token usage event type"
    )
    prompt_tokens: int = Field(..., description="Number of prompt tokens used")
    completion_tokens: int = Field(..., description="Number of completion tokens used")
    total_tokens: int = Field(..., description="Total number of tokens used")
    model: str = Field(..., description="Model name used")

    def to_sse_format(self) -> str:
        """Convert to SSE format for streaming"""
        return f"event: token_usage\ndata: {self.model_dump_json()}\n\n"


class ErrorEvent(ChatEvent):
    """Event for error messages"""

    event_type: EventType = Field(
        default=EventType.ERROR, description="Error event type"
    )
    error_message: str = Field(..., description="Error message to display")

    def to_sse_format(self) -> str:
        """Convert to SSE format for streaming"""
        return f"data: [ERROR]: {self.error_message}\n\n"


class ChatEventFormatter:
    """Utility class to format chat events consistently"""

    @staticmethod
    def format_for_streaming(event: ChatEvent) -> str:
        """Format event for streaming chat (plain text)"""
        if isinstance(event, ContentEvent):
            return event.content
        elif isinstance(event, MetadataEvent):
            # For streaming chat, metadata becomes separate SSE events
            return event.to_sse_format()
        elif isinstance(event, TokenUsageEvent):
            return event.to_sse_format()
        elif isinstance(event, ErrorEvent):
            return event.error_message
        else:
            raise ValueError(f"Unknown event type: {type(event)}")

    @staticmethod
    def format_for_json(event: ChatEvent) -> str:
        """Format event for JSON chat (structured data)"""
        if isinstance(event, ContentEvent):
            # Check if content is already formatted as JSON
            content = event.content
            if content.startswith('{"data":') and content.endswith("}"):
                # Content is already formatted, return as-is (preserve original formatting)
                return content
            else:
                # Content is plain text, wrap in data format with proper JSON escaping
                data_dict = {"data": content}
                return json.dumps(data_dict)
        elif isinstance(event, MetadataEvent):
            # Metadata as JSON string for JSON chat (matching test expectations)
            metadata_dict = {"metadata": {"citations": event.citations or []}}
            if event.metadata:
                metadata_dict["metadata"].update(event.metadata)
            return f"{json.dumps(metadata_dict)}"
        elif isinstance(event, TokenUsageEvent):
            return event.to_sse_format()
        elif isinstance(event, ErrorEvent):
            # Error in JSON format for JSON chat
            error_response = {"data": f"[ERROR]: {event.error_message}"}
            return f"data: {error_response}\n\n"
        else:
            raise ValueError(f"Unknown event type: {type(event)}")


def create_content_event(content: str) -> ContentEvent:
    """Factory function to create content events"""
    return ContentEvent(content=content)


def create_metadata_event(
    citations: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None
) -> MetadataEvent:
    """Factory function to create metadata events"""
    return MetadataEvent(citations=citations, metadata=metadata)


def create_token_usage_event(
    prompt_tokens: int, completion_tokens: int, total_tokens: int, model: str
) -> TokenUsageEvent:
    """Factory function to create token usage events"""
    return TokenUsageEvent(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        model=model,
    )


def create_error_event(error_message: str) -> ErrorEvent:
    """Factory function to create error events"""
    return ErrorEvent(error_message=error_message)
