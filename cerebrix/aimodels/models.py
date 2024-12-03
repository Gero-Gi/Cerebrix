from django.db import models

from .types import LLMTypes

class ChatModel(models.Model):
    """
    This represents a LangChain ChatModel [https://python.langchain.com/docs/concepts/chat_models/]. 
    
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Configuration for the chat model, they will be passed as kwargs to the LangChain ChatModel class
    config = models.JSONField()
    # Secret configuration for the chat model. Here is where you put your API keys for example.
    secret_config = models.JSONField()
    
    # The type of the chat model
    type = models.IntegerField(choices=LLMTypes.choices)
    
    
    def __str__(self):
        return self.name
    
    
