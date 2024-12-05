from django.db import models
from encrypted_json_fields.fields import EncryptedJSONField


from .types import LLMTypes, LLM_TYPE_TO_CHAT_MODEL
from common.models.mixins import TimestampUserModel

class ChatModel(TimestampUserModel):
    """
    This represents a LangChain ChatModel [https://python.langchain.com/docs/concepts/chat_models/]. 
    
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Configuration for the chat model, they will be passed as kwargs to the LangChain ChatModel class
    config = models.JSONField()
    # Secret configuration for the chat model. Here is where you put your API keys for example.
    secret_config = EncryptedJSONField()
    
    # The type of the chat model
    type = models.IntegerField(choices=LLMTypes.choices)
    
    context_window = models.IntegerField(default=0)
    
    
    def __str__(self):
        return self.name
    
    def get_model(self, additional_kwargs={}):
        """
        Get the LangChain ChatModel instance for this ChatModel.
        It handles authentication and other configurations.
        """
        return LLM_TYPE_TO_CHAT_MODEL[self.type](**self.config, **additional_kwargs)
    
    @property
    def model(self):
        return self.get_model()
    
    
