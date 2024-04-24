# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import time
import uuid

from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from shared.document_retriever import DocumentRetrieval
from shared.llm_config import LLMChatFactory, LLMConfig
from shared.logger import TeamAILogger
from shared.services.embeddings_service import EmbeddingsService


class TeamAIBaseChat:
    def __init__(
        self, llm_config: LLMConfig, chat_model: BaseChatModel, system_message: str
    ):
        self.system = system_message
        self.llm_config = llm_config
        if llm_config.supports_system_messages():
            self.memory = [SystemMessage(content=system_message)]
        else:
            self.memory = []
        self.chat_model = chat_model

    def log_run(self, extra={}):
        class_name = self.__class__.__name__
        extra_info = {
            "chat_type": class_name,
            "conversation": {"length": len(self.memory)},
            "model": self.llm_config.service_name,
        }
        extra_info.update(extra)

        TeamAILogger.get().analytics("Sending message", extra_info)

    def memory_as_text(self):
        return "\n".join([str(message) for message in self.memory])


class NonStreamingChat(TeamAIBaseChat):
    def __init__(
        self, llm_config: LLMConfig, system_message: str = "You are a helpful assistant"
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )

    def run(self, message: str):
        self.memory.append(HumanMessage(content=message))
        self.log_run()

        ai_message = self.chat_model(self.memory)
        self.memory.append(AIMessage(content=ai_message.content))

        return ai_message.content

    def start(self, template: PromptTemplate, variables):
        initial_instructions = template.format(**variables)
        if not self.llm_config.supports_system_messages():
            initial_instructions = self.system + initial_instructions
        return self.run(initial_instructions)

    def start_with_prompt(self, prompt: str):
        return self.run(prompt)

    def next(self, human_message):
        return self.run(human_message)


class StreamingChat(TeamAIBaseChat):
    def __init__(
        self, llm_config: LLMConfig, system_message: str = "You are a helpful assistant"
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )

    def run(self, message: str):
        self.memory.append(HumanMessage(content=message))
        self.log_run()

        for i, chunk in enumerate(self.chat_model.stream(self.memory)):
            if i == 0:
                self.memory.append(AIMessage(content=""))
            self.memory[-1].content += chunk.content
            yield chunk.content

    def start(self, template: PromptTemplate, variables={}):
        initial_message = template.format(**variables)
        if not self.llm_config.supports_system_messages():
            initial_message = self.system + initial_message

        chat_history = [[initial_message, ""]]

        for chunk in self.run(initial_message):
            chat_history[-1][1] += chunk
            yield chat_history

    def start_with_prompt(self, prompt: str):
        chat_history = [[prompt, ""]]
        for chunk in self.run(prompt):
            chat_history[-1][1] += chunk
            yield chat_history

    def next(self, human_message, chat_history):
        chat_history += [[human_message, ""]]
        for chunk in self.run(human_message):
            chat_history[-1][1] += chunk
            yield chat_history

    def summarise_conversation(self):
        copy_of_history = []
        copy_of_history.extend(self.memory)
        copy_of_history.append(
            HumanMessage(
                content="""
            Summarise the conversation we've had so far in maximum 2 paragraphs.
            I want to use the summary to start a search for other relevant information for my task,
            so please make sure to include important key words and phrases that would help
            me find relevant information. It is not important that the summary is polished sentences,
            it is more important that a similarity search would find relevant information based on the summary."""
            )
        )
        summary = self.chat_model(copy_of_history)
        return summary.content

    def next_advice_from_knowledge(
        self, chat_history, knowledge_document_key: str, knowledge_domain: str
    ):
        # 1 summarise the conversation so far
        summary = self.summarise_conversation()

        if knowledge_document_key == "all":
            context_documents = EmbeddingsService.similarity_search_with_scores(
                summary, knowledge_domain
            )
        else:
            knwoeldge_document = EmbeddingsService.get_embedded_document(
                knowledge_document_key
            )
            context_documents = (
                EmbeddingsService.similarity_search_on_single_document_with_scores(
                    query=summary,
                    document_key=knwoeldge_document.key,
                    kind=knwoeldge_document.kind,
                )
            )

        context_for_prompt = "\n---".join(
            [f"{document.page_content}" for document, score in context_documents]
        )
        sources = DocumentRetrieval.get_unique_sources(context_documents)
        sources_markdown = (
            "**These articles might be relevant:**\n"
            + "\n".join(
                [f"- [{source['title']}]({source['source']})" for source in sources]
            )
            + "\n\n"
        )

        # 3 continue the conversation and get the advice
        prompt = f"""
        I have a SUMMARY of our conversation so far, and I would like some additional advice and context
        for that conversation, based on the CONTEXT I will provide to you.

        ---- SUMMARY
        {summary}

        ---- CONTEXT
        {context_for_prompt}

        ----
        What else can you tell me based on the conversation summary the knowledge context?
        Do not provide any advice that is out of the context provided.
        """

        chat_history += [
            [f"Give me advice based on the content of '{knowledge_document_key}'", ""]
        ]
        chat_history[-1][1] += sources_markdown
        yield chat_history

        for chunk in self.run(prompt):
            chat_history[-1][1] += chunk
            yield chat_history


class Q_A_ResponseParser:
    feedback_prefix: str = "Answer:"
    question_prefix: str = "Question:"

    def parse(self, text: str) -> str:
        index = text.rfind(f"\n{self.question_prefix}")
        if index != -1:
            return text[index + len(f"\n{self.question_prefix}") :]
        else:
            return text


class Q_A_Chat(TeamAIBaseChat):
    def __init__(
        self, llm_config: LLMConfig, system_message: str = "You are a helpful assistant"
    ):
        super().__init__(
            llm_config,
            LLMChatFactory.new_llm_chat(llm_config, stop="Answer:"),
            system_message,
        )

    def process_response(self, response: str):
        # TODO: How to NOT post-process when the Q&A time is over?
        # TODO: If the Q&A is very long, we could reset the history to only include the Q&A end result in the history, from that point on
        processed_response = Q_A_ResponseParser().parse(response)
        return processed_response

    def run(self, message: str):
        self.memory.append(HumanMessage(content=message))
        self.log_run()

        ai_message = self.chat_model(self.memory)
        processed_response = self.process_response(ai_message.content)
        self.memory.append(AIMessage(content=processed_response))

        return processed_response

    def start(self, template: PromptTemplate, variables):
        initial_instructions = template.format(**variables)
        if not self.llm_config.supports_system_messages():
            initial_instructions = self.system + initial_instructions
        return self.run(initial_instructions)

    def start_with_prompt(self, prompt: str):
        return self.run(prompt)

    def next(self, human_message):
        return self.run(human_message)


class DocumentsChat(TeamAIBaseChat):
    def __init__(
        self,
        llm_config: LLMConfig,
        knowledge: str,
        kind: str,
        system_message: str = "You are a helpful assistant",
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )
        self.kind = kind
        self.knowledge = knowledge
        self.chain = DocumentsChat.create_chain(self.chat_model)

    @staticmethod
    def create_chain(chat_model):
        return load_qa_chain(llm=chat_model, chain_type="stuff")

    def get_source_title(self, source: Document) -> str:
        if "title" in source.metadata:
            return f"[{source.metadata['title']}]({source.metadata['source']})"
        elif "file" in source.metadata:
            return f"{os.path.basename(source.metadata['file'])}"
        else:
            return "unknown"

    def get_source_page(self, source: Document) -> str:
        if "page" in source.metadata:
            return source.metadata["page"]
        else:
            return "NA"

    def run(self, message: str):
        self.log_run({"knowledge": self.knowledge})
        self.memory.append(HumanMessage(content=message))

        if self.knowledge == "all":
            search_results = EmbeddingsService.similarity_search_with_scores(
                query=message, kind=self.kind
            )
        else:
            search_results = (
                EmbeddingsService.similarity_search_on_single_document_with_scores(
                    query=message, document_key=self.knowledge, kind=self.kind
                )
            )

        documents = [document for document, _ in search_results]

        template = self.build_prompt(message)

        ai_message = self.chain({"input_documents": documents, "question": template})
        self.memory.append(AIMessage(content=ai_message["output_text"]))

        sources_markdown = (
            "**These articles were searched as input to try and answer the question:**\n"
            + "\n".join(
                [
                    f"- {self.get_source_title(document)} (page {self.get_source_page(document)})"
                    for document in documents
                ]
            )
        )
        self.memory.append(AIMessage(content=sources_markdown))

        return ai_message["output_text"], sources_markdown

    def build_prompt(self, question) -> str:
        return (
            """Provide information over the following pieces of CONTEXT to answer the QUESTION at the end.
        
        CONTEXT:
        ```
        {context}
        ```
        QUESTION:
        ```
        In that CONTEXT, consider the following question: """
            + question
            + """
        ```
        
        You can only answer based on the provided context. If an answer cannot be formed strictly using the context, 
        say you cannot find information about that topic in the given context.
        
        Please provide an answer to the question based on the context in Markdown format.
        """
        )

    def next(self, human_message):
        return self.run(human_message)


class ServerChatSessionMemory:
    def __init__(self):
        self.USER_CHATS = {}

    def clear_old_entries(self):
        allowed_age_in_minutes = 30
        allowed_age_in_seconds = 60 * allowed_age_in_minutes
        print(
            f"CLEANUP: Removing chat sessions with age > {allowed_age_in_minutes} mins from memory. Currently {len(self.USER_CHATS)} entries in memory"
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

        TeamAILogger.get().analytics(
            f"Creating a new chat session for category {category} with key {session_key} for user {user_identifier}"
        )
        self.USER_CHATS[session_key] = {
            "created_at": time.time(),
            "last_access": time.time(),
            "user": user_identifier,
            "chat": None,
        }
        return session_key

    def store_chat(self, session_key: str, chat_session: TeamAIBaseChat):
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

        chat_session: TeamAIBaseChat = chat_session_data["chat"]
        return chat_session.memory_as_text()
