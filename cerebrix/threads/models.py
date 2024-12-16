from django.db import models
import json

from common.models.mixins import TimestampUserModel, TimestampModel
from .types import MessageRole, MessageContentType, MemoryType

from .managers import ThreadManager, ThreadMessageManager
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class ThreadBackend(TimestampUserModel):
    """
    Base model that defines the properties required to initialize and manage a Thread.
    """

    name = models.CharField(max_length=255)
    chat_model = models.ForeignKey(
        "aimodels.ChatModel", on_delete=models.SET_NULL, null=True
    )

    # System message that defines the AI assistant's behavior for all threads using this backend
    system_message = models.TextField(blank=True, null=True)

    memory_type = models.CharField(
        max_length=20, choices=MemoryType.choices, default=MemoryType.NONE
    )
    # percentage of context window size to use as memory
    memory_size = models.SmallIntegerField(default=0)
    # number of messages to keep in short term memory -> the last messages to be sent to the model
    short_term_memory_size = models.SmallIntegerField(default=20)

    def __str__(self):
        return self.name
    
    @property
    def memory_size_tokens(self):
        return self.memory_size / 100 * self.chat_model.context_window


class Thread(TimestampModel):
    """
    This model represents a Thread linked to a ThreadBackedModel and a User.
    """

    backend = models.ForeignKey(
        ThreadBackend, on_delete=models.SET_NULL, null=True, related_name="threads"
    )
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    # System message that defines the AI assistant's behavior for this thread
    # if it's not defined, the backend's system message will be used
    system_message = models.TextField(blank=True, null=True)

    name = models.CharField(max_length=255, blank=True, null=True)

    # Summary of the messages in the thread. It's used when the memory type is set to SUMMARY
    summary = models.TextField(blank=True, null=True)

    objects = ThreadManager()

    def __str__(self):
        return self.name or f"Thread {self.id}"


class ThreadMessage(TimestampModel):
    """
    Represents a message within a Thread, supporting both text and multimodal content.

    The message content is always stored as a JSON field, and the content type determines how it's interpreted.
    The json always have one key: value, which is the actual content of the message that depends on the content type:
        - text: <str>
        - multimodal: <dict>
        - prompt: <dict>

    The content type used depends on the capabilities of the associated ChatModel
    and ThreadBacked configuration.
    """

    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )

    content_type = models.CharField(max_length=20, choices=MessageContentType.choices)
    content = models.JSONField(default=None, blank=True, null=True)

    role = models.CharField(max_length=20, choices=MessageRole.choices)

    metadata = models.JSONField(default=None, blank=True, null=True)

    # number of tokens in the message content - not the actual content sent to the model
    content_tokens = models.IntegerField(default=0)
    # total number of tokens in the message - includes all the actual tokens sent to the model
    # content + memory + prompt + rag + ...
    # this value is taken from the ChatModelResponse object
    total_tokens = models.IntegerField(default=0)
    # NOTE: these values are equal when the role is ASSISTANT since the content is the response 
    # of the model without any additional info
    

    objects = ThreadMessageManager()
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_role_display()} - {self.created_at}"

    def save(self, *args, **kwargs):
        if self.content_type == MessageContentType.TEXT:
            self.tokens = self.thread.backend.chat_model.count_tokens(
                self.content.get("value")
            )
        elif self.content_type == MessageContentType.PROMPT:
            self.tokens = self.thread.backend.chat_model.count_tokens(
                json.dumps(self.content.get("value"))
            )

        super().save(*args, **kwargs)

    @property
    def content_value(self):
        return self.content.get("value")

    def set_content_value(self, value):
        self.content = {"value": value}
        
    def get_message(self):
        if self.role == MessageRole.HUMAN:
            return HumanMessage(content=self.content_value, content_tokens=self.content_tokens)
        elif self.role == MessageRole.AI:
            return AIMessage(content=self.content_value, content_tokens=self.content_tokens)
        elif self.role == MessageRole.SYSTEM:
            return SystemMessage(content=self.content_value, content_tokens=self.content_tokens)
        elif self.role == MessageRole.SUMMARIZER:
            return SystemMessage(content=self.content_value, content_tokens=self.content_tokens)
