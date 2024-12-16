from django.db import models


DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE = "You are a helpful assistant."

class MessageRole(models.TextChoices):
    SYSTEM = "system", "System"
    HUMAN = "human", "Human"
    AI = "ai", "Assistant"
    # this is a special role used to summarize the thread
    # when creating the actual message containing the summary, the system message is used
    SUMMARIZER = "summarizer", "Summarizer"
    
    
class MessageContentType(models.TextChoices):
    TEXT = "text", "Text"
    MULTIMODAL = "multimodal", "Multimodal"
    PROMPT = "prompt", "Prompt"
    
    
class MemoryType(models.TextChoices):
    NONE = "none", "None"
    BASIC = "basic", "Basic" # All messages in the thread (context window strategy may be used)
    SIMPLE = "simple", "Simple" # A summary of the thread plus the latest messages
    # ADVANCED = "advanced", "Advanced" # Previous strategy, but using a vector store too
    

