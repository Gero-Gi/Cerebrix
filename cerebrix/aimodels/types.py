from django.db import models

from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI


class LLMTypes(models.IntegerChoices):
    """
    The types of LLMs that are supported by the system.
    """
    OPENAI = 1, "OpenAI"
    OLLAMA = 2, "Ollama"

# mapping between the types and the corresponding LangChain ChatModel class
LLM_TYPE_TO_CHAT_MODEL = {
    # LLMTypes.OPENAI: ChatOpenAI,
    LLMTypes.OLLAMA: ChatOllama,
}
