import logging
from langchain_core.messages.utils import trim_messages

from .models import Thread, ThreadBackend, ThreadMessage
from .types import DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE, MessageRole, MessageContentType, MemoryType
from common.utils import get_input_tokens, get_output_tokens

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
        return 100 / self.thread.memory_size * self.chat_model.context_window

    @property
    def memory_type(self):
        return self.thread.memory_type
    
    
    

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

        tokens = self.thread.backend.chat_model.count_tokens(system_message)
        msg = ThreadMessage.objects.create(
            thread=self.thread,
            role=MessageRole.SYSTEM,
            content=system_message,
            total_tokens=tokens,
            content_tokens=tokens,
        )
        
        
    def get_memory(self):
        # return the last messages in the thread, starting from the first human message
        # the number of messages depends on the number of tokens in the messages
        if self.memory_type == MemoryType.BASIC:
            messages = self.thread.messages.filter(role__in=[MessageRole.USER, MessageRole.AI])
            tokens = 0
            history = []
            for message in messages:
                tokens += message.content_tokens
                history.append(message.get_message())
                if tokens >= self.memory_size and message.role == MessageRole.USER:
                    break
            return history, tokens
        
        # return last summary, if available, and messages after the summary
        # if the context window is too big, start a task to generate another summary
        # NOTE: the task will be executed in the background, for this reason:
        #   - the summary is not guaranteed to be up to date
        #   - to prevent race conditions, if a summary is being generated, 
        #     the backend.memory_size may not be respected
        elif self.memory_type == MemoryType.SIMPLE:
            return self.thread.messages.order_by("-created_at")[:self.memory_size]
        
        return [], 0

    def send_message(self, message: str):
        # get last system message
        last_system_message = (
            self.thread.messages.filter(role=MessageRole.SYSTEM)
            .order_by("-created_at")
            .first()
        )

        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", last_system_message.content_value),
                ("human", "{input}"),
            ]
        )
        runnable = chat_prompt | self.thread.backend.chat_model.get_model(max_tokens=20)
        try:
            # send the message to the model
            resp = runnable.invoke({"input": message}, max_tokens='200')

            ThreadMessage.objects.create(
                thread=self.thread,
                role=MessageRole.USER,
                content=message,
                content_type=MessageContentType.TEXT,
                total_tokens=get_input_tokens(
                    resp
                ),  # these are the actual tokens sent to the model
                content_tokens=self.thread.backend.chat_model.count_tokens(message),
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
