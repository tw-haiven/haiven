
# Codebase overview

This is a high level overview of how the (Python) code is structured, as of the time of committing this. It's not fully complete, but shows the components that are most important to understand the structure. 

First, an overview of the main shared components

* "KP Files" stands for "Knowledge Pack Files", i.e. that component is loading files from the knowledge pack
* All of these are getting wired together in [`App`](../app/app.py).


```mermaid
%%{init: {'theme': 'neutral' } }%%

graph TD;

    subgraph Config
        ConfigService
        ConfigService --> FilesystemConfig[config.yaml]
    end

    subgraph LLMs
        ChatClientFactory --> |creates| BaseChatModel[langchain_core...BaseChatModel]
        ChatClientConfig
        ImageDescriptionService
    end

    ChatClientFactory --> ConfigService

    subgraph Knowledge
        KnowledgeManager
        KnowledgeManager --> |creates| KnowledgeBaseMarkdown
        
        KnowledgeBaseMarkdown --> FilesystemKnowledge[KP Files]
        KnowledgeManager --> |creates| KnowledgeBaseDocuments
        KnowledgeManager --> |creates| KnowledgePack
        KnowledgeBaseDocuments --> FilesystemKnowledge
        KnowledgeBaseDocuments --> EmbeddingsClient
        KnowledgeBaseDocuments --> InMemoryEmbeddingsDB
        InMemoryEmbeddingsDB --> FAISS
        
        InMemoryEmbeddingsDB --> |*| DocumentEmbedding
        KnowledgePack -->|**| KnowledgeContext
    end

    KnowledgeManager --> ConfigService

    subgraph Prompts
        PromptsFactory --> |create| PromptList
        PromptList --> FilesystemPrompts[KP Files]
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

    style BaseChatModel fill:lightyellow
    style FilesystemPrompts fill:lightgreen
    style FilesystemKnowledge fill:lightgreen
    style FilesystemConfig fill:lightgreen
    style FAISS fill:lightblue
    
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