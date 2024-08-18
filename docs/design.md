
# Codebase overview

This is a high level overview of how the (Python) code is structured, as of the time of committing this. It's not fully complete, but shows the components that are most important to understand the structure.

First, an overview of the main shared components:

```mermaid
%%{init: {'theme': 'neutral' } }%%

graph TD;

    subgraph Config
        ConfigService
    end

    subgraph LLMs
        ChatClientFactory --> |creates| BaseChatModel[langchain_core...BaseChatModel]
        style BaseChatModel fill:lightyellow
        ChatClientConfig
        ImageDescriptionService
    end

    ChatClientFactory --> ConfigService

    
    subgraph Knowledge
        KnowledgeManager
        KnowledgeManager --> |creates| KnowledgeBaseMarkdown
        KnowledgeManager --> |creates| KnowledgeBaseDocuments
        KnowledgeManager --> |creates| KnowledgePack
        KnowledgeBaseDocuments --> EmbeddingsClient
        KnowledgeBaseDocuments --> InMemoryEmbeddingsDB
        InMemoryEmbeddingsDB --> |*| DocumentEmbedding
        KnowledgePack -->|**| KnowledgeContext
    end

    KnowledgeManager --> ConfigService

    subgraph Prompts
        PromptsFactory --> |create| PromptList
    end

    subgraph Chats
        ChatManager
        ChatManager --> ServerChatSessionMemory
        
        ChatManager --> |creates| DocumentsChat
        ChatManager --> |creates| JSONChat
        ChatManager --> |creates| StreamingChat
        ChatManager --> |creates| QAChat
    end

    ChatManager --> ConfigService
    ChatManager --> ChatClientFactory
    ChatManager --> KnowledgeManager

    DocumentsChat --> KnowledgeManager
    StreamingChat --> KnowledgeManager
    JSONChat --> KnowledgeManager

    ImageDescriptionService --> ConfigService
    
```

We currently have two consumers of those main components, the Gradio UI, and the API used by the "Guided mode" React frontend:

```mermaid
%%{init: {'theme': 'neutral' } }%%

graph TD;

    subgraph API
        BobaApi
        BobaApi --> |creates| ApiBasics
        BobaApi --> |creates| Api...
    end

    subgraph GradioUI
        UIFactory
        UIFactory --> |creates| UIPrompts[UI for prompts chat]
        UIFactory --> |creates| UIBrains[UI for brainstorming chat]
        UIFactory --> |creates| UIMore[UI for ...]
    end

    subgraph Shared

        BobaApi --> PromptsFactory
        BobaApi --> KnowledgeManager
        BobaApi --> ChatManager
        BobaApi --> ConfigService

        UIFactory --> PromptsFactory
        UIFactory --> KnowledgeManager
        UIFactory --> ChatManager
        
        UIFactory --> ImageDescriptionService

    end
```