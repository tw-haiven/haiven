import json
import time
import uuid

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from shared.documents_utils import DocumentsUtils
from shared.llm_config import LLMChatFactory, LLMConfig
from shared.logger import HaivenLogger
from shared.services.embeddings_service import EmbeddingsService


class HaivenBaseChat:
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

        HaivenLogger.get().analytics("Sending message", extra_info)

    def memory_as_text(self):
        return "\n".join([str(message) for message in self.memory])


class NonStreamingChat(HaivenBaseChat):
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


class StreamingChat(HaivenBaseChat):
    def __init__(
        self,
        llm_config: LLMConfig,
        system_message: str = "You are a helpful assistant",
        stream_in_chunks: bool = False,
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )
        self.stream_in_chunks = stream_in_chunks

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
            if self.stream_in_chunks:
                yield chunk
            else:
                yield chat_history

    def start_with_prompt(self, prompt: str):
        chat_history = [[prompt, ""]]
        for chunk in self.run(prompt):
            chat_history[-1][1] += chunk
            if self.stream_in_chunks:
                yield chunk
            else:
                yield chat_history

    def next(self, human_message, chat_history=[]):
        chat_history += [[human_message, ""]]
        for chunk in self.run(human_message):
            if self.stream_in_chunks:
                yield chunk
            else:
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
        self, chat_history, knowledge_document_key: str, knowledge_context: str
    ):
        # 1 summarise the conversation so far
        summary = self.summarise_conversation()

        if knowledge_document_key == "all":
            context_documents = EmbeddingsService.similarity_search(
                summary, knowledge_context
            )
        else:
            knwoeldge_document = EmbeddingsService.get_embedded_document(
                knowledge_document_key
            )
            context_documents = EmbeddingsService.similarity_search_on_single_document(
                query=summary,
                document_key=knwoeldge_document.key,
                context=knwoeldge_document.context,
            )

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
    question_prefix: str = "<Question>"
    feedback_prefix: str = "<Answer>"

    def parse(self, text: str) -> str:
        text = text.replace("</Question>", "")
        text = text.replace("</Answer>", "")
        question_index = text.rfind(f"\n{self.question_prefix}")
        answer_index = text.rfind(f"\n{self.feedback_prefix}")
        if question_index != -1 and answer_index != -1:
            question = text[
                question_index + len(f"\n{self.question_prefix}") : answer_index
            ]
            suggested_answer = text[answer_index + len(f"\n{self.feedback_prefix}") :]
            return f"**Question:** {question}\n\n**Suggested answer:** {suggested_answer}\n\nSay 'ok' or provide your own answer."
        else:
            return text


class Q_A_Chat(HaivenBaseChat):
    def __init__(
        self, llm_config: LLMConfig, system_message: str = "You are a helpful assistant"
    ):
        super().__init__(
            llm_config,
            LLMChatFactory.new_llm_chat(llm_config, stop="</Answer>"),
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


class DocumentsChat(HaivenBaseChat):
    def __init__(
        self,
        llm_config: LLMConfig,
        knowledge: str,
        context: str,
        system_message: str = "You are a helpful assistant",
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )
        self.context = context
        self.knowledge = knowledge
        self.chain = DocumentsChat.create_chain(self.chat_model)

    @staticmethod
    def create_chain(chat_model):
        return load_qa_chain(llm=chat_model, chain_type="stuff")

    def run(self, message: str):
        self.log_run({"knowledge": self.knowledge})
        self.memory.append(HumanMessage(content=message))

        if self.knowledge == "all":
            search_results = EmbeddingsService.similarity_search(
                query=message, context=self.context, k=10
            )
        else:
            search_results = EmbeddingsService.similarity_search_on_single_document(
                query=message, document_key=self.knowledge, context=self.context
            )

        template = self.build_prompt(message)

        ai_message = self.chain(
            {"input_documents": search_results, "question": template}
        )
        self.memory.append(AIMessage(content=ai_message["output_text"]))

        de_duplicated_sources = DocumentsUtils.get_unique_sources(search_results)

        sources_markdown = (
            "**These sources were searched as input to try and answer the question:**\n"
            + "\n".join(
                [
                    f"- {DocumentsUtils.get_search_result_item(document.metadata)}"
                    for document in de_duplicated_sources
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


class JSONChat(HaivenBaseChat):
    def __init__(
        self,
        llm_config=LLMConfig("azure-gpt4", 0.2),
        system_message: str = "You are a helpful assistant",
        event_stream_standard=True,
    ):
        super().__init__(
            llm_config, LLMChatFactory.new_llm_chat(llm_config), system_message
        )
        # Transition to new frontend SSE implementation: Add "data: " and "[DONE]" vs not doing that
        self.event_stream_standard = event_stream_standard

    def stream_from_model(self, prompt):
        client = LLMChatFactory.new_llm_chat(self.llm_config)
        messages = [HumanMessage(content=prompt)]
        stream = client.stream(messages)
        for chunk in stream:
            yield chunk.content

        if self.event_stream_standard:
            yield "[DONE]"

    def run(self, message: str):
        self.memory.append(HumanMessage(content=message))
        data = enumerate(self.stream_from_model(message))
        for i, chunk in data:
            if i == 0:
                self.memory.append(AIMessage(content=""))

            if chunk == "[DONE]":
                yield f"data: {chunk}\n\n"
            else:
                self.memory[-1].content += chunk
                if self.event_stream_standard:
                    message = '{ "data": ' + json.dumps(chunk) + " }"
                    yield f"data: {message}\n\n"
                else:
                    message = json.dumps({"data": chunk})
                    yield f"{message}\n\n"


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
