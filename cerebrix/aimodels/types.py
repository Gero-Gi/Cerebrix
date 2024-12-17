from django.db import models

from langchain_ollama import ChatOllama, OllamaLLM
# from langchain_openai import ChatOpenAI
from langchain_core.language_models.fake_chat_models import FakeChatModel

class LLMTypes(models.IntegerChoices):
    """
    The types of LLMs that are supported by the system.
    """
    OPENAI = 1, "OpenAI"
    OLLAMA = 2, "Ollama"
    FAKE = 99, "Fake" # used for testing

# mapping between the types and the corresponding LangChain ChatModel class
LLM_TYPE_TO_CHAT_MODEL = {
    # LLMTypes.OPENAI: ChatOpenAI,
    LLMTypes.OLLAMA: ChatOllama,
}

# Mapping between the types and the corresponding LangChain LLM class
LLM_TYPE_TO_LLM = {
    LLMTypes.OLLAMA: OllamaLLM,
}
