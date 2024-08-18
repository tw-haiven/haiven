
# Codebase overview

This is a high level overview of how the (Python) code is structured, as of the time of committing this. It's not fully complete, but shows the components that are most important to understand the structure.

```mermaid

graph TD;

    subgraph Config
        ConfigService
    end
    
    subgraph Knowledge
        KnowledgeManager --> ConfigService
        KnowledgeManager --> |creates| KnowledgeBaseMarkdown
        KnowledgeManager --> |creates| KnowledgeBaseDocuments
        KnowledgeManager --> |creates| KnowledgePack
        KnowledgeBaseDocuments --> EmbeddingsClient
        KnowledgeBaseDocuments --> InMemoryEmbeddingsDB
        InMemoryEmbeddingsDB --> |*| DocumentEmbedding
        KnowledgePack -->|**| KnowledgeContext
    end

    subgraph Prompts
        PromptsFactory --> |create| PromptList
    end

    subgraph LLMs
        ChatClientFactory
        ChatClientConfig
        ImageDescriptionService
    end

    subgraph Chats
        ChatClientFactory --> ConfigService

        ChatManager --> |creates| DocumentsChat
        ChatManager --> |creates| JSONChat
        ChatManager --> |creates| StreamingChat
        ChatManager --> |creates| QAChat

        ChatManager --> ConfigService
        ChatManager --> ServerChatSessionMemory
        ChatManager --> ChatClientFactory
        ChatManager --> KnowledgeManager
        

        DocumentsChat --> KnowledgeManager
        StreamingChat --> KnowledgeManager
        JSONChat --> KnowledgeManager
        QAChat
    end

    subgraph API
        BobaApi --> PromptsFactory
        BobaApi --> KnowledgeManager
        BobaApi --> ChatManager
        BobaApi --> ConfigService
        BobaApi --> |creates| ApiBasics
        BobaApi --> |creates| ApiThreatModelling
        BobaApi --> |creates| ApiRequirementsBreakdown
    end

    subgraph GradioUI
        UIFactory --> PromptsFactory
        UIFactory --> KnowledgeManager
        UIFactory --> ChatManager
    end
    
    UIFactory --> ImageDescriptionService
    ImageDescriptionService --> ConfigService
    
```