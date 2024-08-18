
# Codebase overview

This is a high level overview of how the (Python) code is structured, as of the time of committing this. It's not fully complete, but shows the components that are most important to understand the structure.

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

    subgraph API
        BobaApi
        BobaApi --> |creates| ApiBasics
        BobaApi --> |creates| ApiThreatModelling
        BobaApi --> |creates| ApiRequirementsBreakdown
    end

    BobaApi --> PromptsFactory
    BobaApi --> KnowledgeManager
    BobaApi --> ChatManager
    BobaApi --> ConfigService

    subgraph GradioUI
        UIFactory
    end

    UIFactory --> PromptsFactory
    UIFactory --> KnowledgeManager
    UIFactory --> ChatManager
    
    UIFactory --> ImageDescriptionService
    ImageDescriptionService --> ConfigService
    
```