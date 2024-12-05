from django.db import models


DEFAULT_CHAT_MODEL_SYSTEM_MESSAGE = "You are a helpful assistant."

class MessageRole(models.TextChoices):
    SYSTEM = "system", "System"
    USER = "user", "User"
    AI = "ai", "Assistant"
    SUMMARY = "summary", "Summary"
    
    
class MessageContentType(models.TextChoices):
    TEXT = "text", "Text"
    MULTIMODAL = "multimodal", "Multimodal"
    PROMPT = "prompt", "Prompt"
    
    
class MemoryType(models.TextChoices):
    NONE = "none", "None"
    HISTORY = "history", "History" # All messages in the thread (context window strategy may be used)
    SUMMARY = "summary", "Summary" # A summary of the thread plus the latest messages

# Keys used (commonly) to get the number of tokens of the input from the LLM response metadata
INPUT_TOKENS_KEYS = ["input_tokens", "prompt_tokens_count", "prompt_tokens"]
# Keys used (commonly) to get the number of tokens of the output from the LLM response metadata
OUTPUT_TOKENS_KEYS = ["completion_tokens", "output_tokens", "candidates_token_count"]