from django.db import models

from langchain_ollama import ChatOllama, OllamaLLM, OllamaEmbeddings
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
)
# from langchain_openai import ChatOpenAI
from langchain_core.language_models.fake_chat_models import FakeChatModel

class LLMTypes(models.IntegerChoices):
    """
    The types of LLMs that are supported by the system.
    """
    OPENAI = 1, "OpenAI"
    OLLAMA = 2, "Ollama"
    MISTRAL = 3, "Mistral"
    FAKE = 99, "Fake" # used for testing

# mapping between the types and the corresponding LangChain ChatModetestl class
LLM_TYPE_TO_CHAT_MODEL = {
    # LLMTypes.OPENAI: ChatOpenAI,
    LLMTypes.OLLAMA: ChatOllama,
    LLMTypes.MISTRAL: ChatMistralAI,
}

# Mapping between the types and the corresponding LangChain LLM class
LLM_TYPE_TO_LLM = {
    LLMTypes.OLLAMA: OllamaLLM,
}

class EmbeddingModelTypes(models.IntegerChoices):
    """
    The types of embedding models that are supported by the system.
    """
    OPENAI = 1, "OpenAI"
    OLLAMA = 2, "Ollama"
    MISTRAL = 3, "Mistral"
    FAKE = 99, "Fake" # used for testing

# mapping between the types and the corresponding LangChain EmbeddingModel class
EMBEDDING_MODEL_TYPE_TO_EMBEDDING_MODEL = {
    # EmbeddingModelTypes.OPENAI: OpenAIEmbeddings,
    EmbeddingModelTypes.OLLAMA: OllamaEmbeddings,
    EmbeddingModelTypes.MISTRAL: MistralAIEmbeddings,
}