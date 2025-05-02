# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import time
import uuid
from typing import List

from pydantic import BaseModel
from config_service import ConfigService
from knowledge_manager import KnowledgeManager
from embeddings.documents import DocumentsUtils
from llms.clients import (
    ChatClient,
    ChatClientFactory,
    HaivenAIMessage,
    HaivenHumanMessage,
    HaivenSystemMessage,
    ModelConfig,
)
from logger import HaivenLogger


class HaivenBaseChat:
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        self.knowledge_manager = knowledge_manager
        self.system = knowledge_manager.get_system_message()
        aggregatedContext = (
            knowledge_manager.knowledge_base_markdown.aggregate_all_contexts(
                contexts, user_context
            )
        )
        if aggregatedContext:
            self.system += (
                "\n\nMultiple contexts will be given. Consider "
                + "all contexts when responding to the given prompt "
                + aggregatedContext
            )

        self.memory = [HaivenSystemMessage(content=self.system)]
        self.chat_client = chat_client

    def log_run(self, extra={}):
        class_name = self.__class__.__name__
        extra_info = {
            "chat_type": class_name,
            "numberOfMessages": len(self.memory),
        }
        extra_info.update(extra)

        HaivenLogger.get().analytics("Sending message", extra_info)

    def memory_as_text(self):
        return "\n".join([str(message) for message in self.memory])

    def _similarity_query(self, message):
        if len(self.memory) == 1:
            return message

        if len(self.memory) > 5:
            conversation = "\n".join(
                [message.content for message in (self.memory[:2] + self.memory[-4:])]
            )
        else:
            conversation = "\n".join([message.content for message in self.memory])

        system_message = f"""You are a helpful assistant.
        Your task is create a single search query to find relevant information, based on the conversation and the current user message.
        Rules: 
        - Search query should find relevant information for the current user message only.
        - Include all important key words and phrases in query that would help to search for relevant information.
        - If the current user message does not need to search for additional information, return NONE.
        - Only return the single standalone search query or NONE. No explanations needed.
        
        Conversation:
        {conversation}
        """
        prompt = [HaivenSystemMessage(content=system_message)]
        prompt.append(
            HaivenHumanMessage(content=f"Current user message: {message} \n Query:")
        )

        stream = self.chat_client.stream(prompt)
        query = ""
        for chunk in stream:
            query += chunk.get("content", "")

        if "none" in query.lower():
            return None
        elif "query:" in query.lower():
            return query.split("query:")[1].strip()
        else:
            return query

    def _similarity_search_based_on_history(self, message, knowledge_document_keys):
        similarity_query = self._similarity_query(message)
        print("Similarity Query:", similarity_query)
        if similarity_query is None:
            return None, None

        if knowledge_document_keys:
            context_documents = self.knowledge_manager.knowledge_base_documents.similarity_search_on_multiple_documents(
                query=similarity_query,
                document_keys=knowledge_document_keys,
            )
        else:
            return None, None

        context_for_prompt = "\n---".join(
            [f"{document.page_content}" for document in context_documents]
        )
        de_duplicated_sources = DocumentsUtils.get_unique_sources(context_documents)
        sources_markdown = (
            "**These articles might be relevant:**\n"
            + "\n".join(
                [
                    f"- {DocumentsUtils.get_search_result_item(source.metadata)}"
                    for source in de_duplicated_sources
                ]
            )
            + "\n\n"
        )

        return context_for_prompt, sources_markdown


class StreamingChat(HaivenBaseChat):
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        stream_in_chunks: bool = False,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        super().__init__(chat_client, knowledge_manager, contexts, user_context)
        self.stream_in_chunks = stream_in_chunks

    def run(self, message: str, user_query: str = None):
        self.memory.append(HaivenHumanMessage(content=message))
        try:
            for i, chunk in enumerate(self.chat_client.stream(self.memory)):
                if i == 0:
                    if user_query:
                        self.memory[-1].content = user_query
                    self.memory.append(HaivenAIMessage(content=""))
                self.memory[-1].content += chunk.get("content", "")
                yield chunk.get("content", "")

        except Exception as error:
            if not str(error).strip():
                error = "Error while the model was processing the input"
            print(f"[ERROR]: {str(error)}")
            yield f"[ERROR]: {str(error)}"

    def run_with_document(
        self,
        knowledge_document_keys: List[str],
        message: str = None,
    ):
        try:
            context_for_prompt, sources_markdown = (
                self._similarity_search_based_on_history(
                    message, knowledge_document_keys
                )
            )

            user_request = (
                message
                or "Based on our conversation so far, what do you think is relevant to me with the CONTEXT information I gathered?"
            )

            if context_for_prompt:
                prompt = f"""
                {user_request}
                ---- Here is some additional CONTEXT that might be relevant to this:
                {context_for_prompt} 
                -------
                Do not provide any advice that is outside of the CONTEXT I provided.
                """
            else:
                prompt = user_request

            for chunk in self.run(prompt, user_request):
                yield chunk, sources_markdown

        except Exception as error:
            if not str(error).strip():
                error = "Error while the model was processing the input"
            print(f"[ERROR]: {str(error)}")
            yield f"[ERROR]: {str(error)}", ""


class JSONChat(HaivenBaseChat):
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        super().__init__(chat_client, knowledge_manager, contexts, user_context)

    def stream_from_model(self, new_message):
        try:
            self.memory.append(HaivenHumanMessage(content=new_message))
            stream = self.chat_client.stream(self.memory)
            for chunk in stream:
                if "content" in chunk:
                    yield chunk.get("content", "")
                elif "metadata" in chunk:
                    yield chunk

        except Exception as error:
            if not str(error).strip():
                error = "Error while the model was processing the input"
            print(f"[ERROR]: {str(error)}")
            yield f"[ERROR]: {str(error)}"

    def run(self, message: str):
        def create_data_chunk(chunk):
            message = json.dumps({"data": chunk})
            return f"{message}\n\n"

        try:
            data = enumerate(self.stream_from_model(message))
            for i, chunk in data:
                if "metadata" in chunk:
                    yield json.dumps(chunk)
                else:
                    if i == 0:
                        self.memory.append(HaivenAIMessage(content=""))

                    self.memory[-1].content += chunk
                    yield create_data_chunk(chunk)

        except Exception as error:
            if not str(error).strip():
                error = "Error while the model was processing the input"
            print(f"[ERROR]: {str(error)}")
            yield f"[ERROR]: {str(error)}"


class ServerChatSessionMemory:
    def __init__(self):
        self.USER_CHATS = {}

    def clear_old_entries(self):
        allowed_age_in_minutes = 30
        allowed_age_in_seconds = 60 * allowed_age_in_minutes
        print(
            f"CLEANUP: Removing chat sessions with last user access > {allowed_age_in_minutes} mins from memory. Currently {len(self.USER_CHATS)} entries in memory"
        )

        entries_to_remove = list(
            filter(
                lambda key: self.USER_CHATS[key]["last_access"]
                < time.time() - allowed_age_in_seconds,
                self.USER_CHATS,
            )
        )

        for key in entries_to_remove:
            print("CLEANUP: Removing entry", key)
            del self.USER_CHATS[key]

    def add_new_entry(self, category: str, user_identifier: str):
        # Currently the crude rhythm of checking for old entries: whenever a new one gets created
        self.clear_old_entries()

        session_key = category + "-" + str(uuid.uuid4())

        HaivenLogger.get().analytics(
            f"Creating a new chat session for category {category} with key {session_key} for user {user_identifier}"
        )
        self.USER_CHATS[session_key] = {
            "created_at": time.time(),
            "last_access": time.time(),
            "user": user_identifier,
            "chat": None,
        }
        return session_key

    def store_chat(self, session_key: str, chat_session: HaivenBaseChat):
        self.USER_CHATS[session_key]["chat"] = chat_session

    def get_chat(self, session_key: str):
        if session_key not in self.USER_CHATS:
            raise ValueError(
                f"Invalid identifier {session_key}, your chat session might have expired"
            )
        self.USER_CHATS[session_key]["last_access"] = time.time()
        return self.USER_CHATS[session_key]["chat"]

    def delete_entry(self, session_key):
        if session_key in self.USER_CHATS:
            print("Discarding a chat session from memory", session_key)
            del self.USER_CHATS[session_key]

    def get_or_create_chat(
        self,
        fn_create_chat,
        chat_session_key_value: str = None,
        chat_category: str = "unknown",
        user_identifier: str = "unknown",
    ):
        if chat_session_key_value is None or chat_session_key_value == "":
            chat_session_key_value = self.add_new_entry(chat_category, user_identifier)
            chat_session = fn_create_chat()

            self.store_chat(chat_session_key_value, chat_session)
        else:
            chat_session = self.get_chat(chat_session_key_value)

        return chat_session_key_value, chat_session

    def dump_as_text(self, session_key: str, user_owner: str):
        chat_session_data = self.USER_CHATS.get(session_key, None)
        if chat_session_data is None:
            return f"Chat session with ID {session_key} not found"
        if chat_session_data["user"] != user_owner:
            return f"Chat session with ID {session_key} not found for this user"

        chat_session: HaivenBaseChat = chat_session_data["chat"]
        return chat_session.memory_as_text()


class ChatOptions(BaseModel):
    category: str = None
    in_chunks: bool = False
    user_identifier: str = None


class ChatManager:
    def __init__(
        self,
        config_service: ConfigService,
        chat_session_memory: ServerChatSessionMemory,
        llm_chat_factory: ChatClientFactory,
        knowledge_manager: KnowledgeManager,
    ):
        self.config_service = config_service
        self.chat_session_memory = chat_session_memory
        self.llm_chat_factory = llm_chat_factory
        self.knowledge_manager = knowledge_manager

    def clear_session(self, session_id: str):
        self.chat_session_memory.delete_entry(session_id)

    def get_session(self, chat_session_key_value):
        return self.chat_session_memory.get_chat(chat_session_key_value)

    def streaming_chat(
        self,
        model_config: ModelConfig,
        session_id: str = None,
        options: ChatOptions = None,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        chat_client = self.llm_chat_factory.new_chat_client(model_config)
        return self.chat_session_memory.get_or_create_chat(
            lambda: StreamingChat(
                chat_client,
                self.knowledge_manager,
                stream_in_chunks=options.in_chunks if options else None,
                contexts=contexts,
                user_context=user_context,
            ),
            chat_session_key_value=session_id,
            chat_category=options.category if options else None,
            user_identifier=options.user_identifier if options else None,
        )

    def json_chat(
        self,
        model_config: ModelConfig,
        session_id: str = None,
        options: ChatOptions = None,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        chat_client = self.llm_chat_factory.new_chat_client(model_config)
        return self.chat_session_memory.get_or_create_chat(
            lambda: JSONChat(
                chat_client, self.knowledge_manager, contexts, user_context
            ),
            chat_session_key_value=session_id,
            chat_category=options.category if options else None,
            user_identifier=options.user_identifier if options else None,
        )
