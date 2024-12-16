from django.db import models
from django.apps import apps


from .types import DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE, MessageRole


class ThreadManager(models.Manager):
    def create(self, **kwargs):
        """
        Override the default create method to add a SystemMessage to the Thread and to
        ensure that the ThreadBackend is provided.
        """

        backend = kwargs.get("backend", None)
        if backend is None:
            raise ValueError("ThreadBackend must be provided")

        thread = super().create(**kwargs)

        # get the system message for this thread
        system_message = kwargs.get("system_message", thread.backend.system_message)
        if not system_message:
            system_message = DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE

        # create the SystemMessage for this thread
        ThreadMessage = apps.get_model("threads", "ThreadMessage")
        ThreadMessage.objects.create(
            thread=thread, role=MessageRole.SYSTEM, content=system_message
        )

        thread.save()
        return thread


class ThreadMessageManager(models.Manager):
    def create(self, **kwargs):
        content = kwargs.pop("content", None)
        content = {"value": content} if content else None
        kwargs["content"] = content
        return super().create(**kwargs)
