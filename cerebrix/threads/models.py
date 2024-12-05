from django.db import models

from common.models.mixins import TimestampUserModel, TimestampModel
from .types import MessageRole, MessageContentType, MemoryType

from .managers import ThreadManager


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
    
    memory_type = models.CharField(max_length=20, choices=MemoryType.choices, default=MemoryType.NONE)

    def __str__(self):
        return self.name


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
    summary_tokens = models.IntegerField(default=0)
    
    # Total tokens used in the thread
    # it's updated on every llm request: both for messages and for other llm calls (e.g. for summarization)
    tokens = models.IntegerField(default=0)

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
    
    # Total tokens used in the message
    tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_role_display()} - {self.created_at}"
    
    



