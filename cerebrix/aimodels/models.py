from django.db import models
from django.conf import settings
from encrypted_json_fields.fields import EncryptedJSONField
import logging

from transformers import AutoTokenizer
import tiktoken

logger = logging.getLogger(__name__)

from .types import (
    LLMTypes,
    LLM_TYPE_TO_CHAT_MODEL,
    LLM_TYPE_TO_LLM,
    EmbeddingModelTypes,
    EMBEDDING_MODEL_TYPE_TO_EMBEDDING_MODEL,
)
from common.models.mixins import TimestampUserModel
from users.models import User


class LanguageModel(TimestampUserModel):
    """
    This represents a LangChain LanguageModel [https://python.langchain.com/docs/concepts/language_models/].

    From this model both ChatModel and LLM can be derived.
    """

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    # Configuration for the chat model, they will be passed as kwargs to the LangChain ChatModel class
    config = EncryptedJSONField()


    # The type of the chat model
    type = models.IntegerField(choices=LLMTypes.choices)

    context_window = models.IntegerField(default=0)

    # The tokenizer to use for this chat model. If None, it will use a non precise tokenizer (word count)
    tokenizer = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_chat_model(self, **kwargs):
        """
        Get the LangChain ChatModel instance for this ChatModel.
        It handles authentication and other configurations.
        """
        return LLM_TYPE_TO_CHAT_MODEL[self.type](**self.config, **kwargs)

    def get_model(self, **kwargs):
        """
        Get the LangChain LLM instance for this LanguageModel.
        It handles authentication and other configurations.
        """
        return LLM_TYPE_TO_LLM[self.type](**self.config, **kwargs)

    @property
    def model(self):
        return self.get_model()

    @property
    def chat_model(self):
        return self.get_chat_model()

    def invoke(self, user: User, *args, **kwargs):
        """
        Invoke the chat model for the given user.
        This method is a wrapper around the chat model's invoke method usefull to better keep track
        of the usage of the chat model for each user.
        """

        # TODO: Add usage tracking
        return self.model.invoke(user, *args, **kwargs)

    def _gpt_tokenizer(self, input: str):
        """
        Use the GPT tokenizer to count the number of tokens in the input string.
        """
        return len(tiktoken.encoding_for_model(self.tokenizer).encode(input))

    def _auto_tokenizer(self, input: str):
        """
        Use the AutoTokenizer to count the number of tokens in the input string.
        """
        tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer, token=settings.HUGGING_FACE_TOKEN
        )
        return len(tokenizer.encode(input))

    def count_tokens(self, input: str):
        """
        Count the number of tokens in the input string for this chat model.
        """
        if not self.tokenizer:
            return self.model.get_num_tokens(input)
        return (
            self._gpt_tokenizer(input)
            if self.type == LLMTypes.OPENAI
            else self._auto_tokenizer(input)
        )


class EmbeddingModel(TimestampUserModel):
    """
    This represents a LangChain EmbeddingModel [https://python.langchain.com/docs/concepts/embedding_models/].
    """

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    # Configuration for the embedding model, they will be passed as kwargs to the LangChain EmbeddingModel class
    config = EncryptedJSONField(blank=True, null=True)

    # The type of the embedding model
    type = models.IntegerField(choices=EmbeddingModelTypes.choices)
    
    # The size of the embedding model. This is used to set the dimension of the vectors in the vector store.
    size = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    @property
    def model(self):
        return self.get_model()

    def get_model(self, **kwargs):
        """
        Get the LangChain EmbeddingModel instance for this EmbeddingModel.
        """
        return EMBEDDING_MODEL_TYPE_TO_EMBEDDING_MODEL[self.type](
            **self.config, **kwargs
        )
        
    def set_size(self):
        self.size = len(self.get_model().embed_query('test'))
    
    def save(self, *args, **kwargs):
        if self.size is None:
            try:
                self.set_size()
            except Exception as e:
                logger.error(f"An error occurred while getting the size of the embedding model: {e}. The model will not work as expected.")
        super().save(*args, **kwargs)
