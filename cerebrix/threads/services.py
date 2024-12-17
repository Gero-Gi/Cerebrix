import logging
from typing import List, Tuple
from langchain_core.messages.utils import trim_messages

from .models import Thread, ThreadBackend, ThreadMessage
from .types import (
    DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE,
    MessageRole,
    MessageContentType,
    MemoryType,
)
from common.utils import get_input_tokens, get_output_tokens
from threads.utils.memory import get_basic_memory, get_simple_memory
from threads.exceptions import TokenLimitExceededError
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from threads.utils import format_message_for_token_count

logger = logging.getLogger("threads.services")


class ThreadService:
    def __init__(self, thread: Thread):
        self.thread = thread

    @property
    def backend(self):
        return self.thread.backend

    @property
    def chat_model(self):
        return self.backend.chat_model

    @property
    def memory_size(self):
        return self.backend.memory_size_tokens

    @property
    def memory_type(self):
        return self.thread.backend.memory_type

    @property
    def messages(self):
        return self.thread.messages.order_by("-created_at")

    def initialize(self):
        """
        Initialize the thread:
        - set the system message if it's not defined
        - create the first system message
        """
        system_message = (
            self.thread.system_message or self.thread.backend.system_message
        )
        if not system_message:
            self.thread.system_message = DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE
            self.thread.save()

        tokens = self.thread.backend.chat_model.count_tokens(
            format_message_for_token_count(system_message, MessageRole.SYSTEM)
        )
        msg = ThreadMessage.objects.create(
            thread=self.thread,
            role=MessageRole.SYSTEM,
            content=system_message,
            total_tokens=tokens,
            content_tokens=tokens,
        )

    def get_memory(self) -> Tuple[List[ThreadMessage], int]:
        # return the last messages in the thread, starting from the first human message
        # the number of messages depends on the number of tokens in the messages
        if self.memory_type == MemoryType.BASIC:
            return get_basic_memory(self.thread)

        elif self.memory_type == MemoryType.SIMPLE:
            return get_simple_memory(self.thread)

        return [], 0

    def send_message(self, message: str):
        # get last system message
        last_system_message = (
            self.thread.messages.filter(role=MessageRole.SYSTEM)
            .order_by("-created_at")
            .first()
        )

        memory, memory_tokens = self.get_memory()
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", last_system_message.content_value),
                MessagesPlaceholder(variable_name="memory"),
                ("human", "{input}"),
            ]
        )
        print(chat_prompt.format(input=message, memory=memory))
        runnable = chat_prompt | self.thread.backend.chat_model.get_chat_model()

        message_tokens = self.thread.backend.chat_model.count_tokens(
            format_message_for_token_count(message, MessageRole.HUMAN)
        )
        try:
            # check if the message + memory is too long to be sent to the model
            tokens_to_send = message_tokens + memory_tokens
            if tokens_to_send > self.backend.chat_model.context_window:
                raise TokenLimitExceededError()

            # send the message to the model
            resp = runnable.invoke(
                {"input": message, "memory": memory}, max_tokens=tokens_to_send
            )

            ThreadMessage.objects.create(
                thread=self.thread,
                role=MessageRole.HUMAN,
                content=message,
                content_type=MessageContentType.TEXT,
                # these are the actual tokens sent to the model
                total_tokens=get_input_tokens(resp),
                content_tokens=message_tokens,
            )

            resp_tokens = get_output_tokens(resp)
            resp_msg = ThreadMessage.objects.create(
                thread=self.thread,
                role=MessageRole.AI,
                content=resp.content,
                content_type=MessageContentType.TEXT,
                total_tokens=resp_tokens,
                content_tokens=resp_tokens,
            )
            return resp_msg

        except Exception as e:
            raise e

    @staticmethod
    def create_thread(backend: ThreadBackend, **kwargs: dict):
        Thread.objects.create(backend=backend, **kwargs)
