from .models import Thread, ThreadBackend, ThreadMessage
from .types import DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE, MessageRole


class ThreadService:
    def __init__(self, thread: Thread):
        self.thread = thread

    
    def initialize(self):
        system_message  = self.thread.system_message or self.thread.backend.system_message
        if not system_message:
            system_message = DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE
            self.thread.save()
        
        ThreadMessage.objects.create(
            thread=self.thread, role=MessageRole.SYSTEM, content=system_message
        )

        
        
    @staticmethod
    def create_thread(backend: ThreadBackend, **kwargs: dict):
        Thread.objects.create(backend=backend, **kwargs)
