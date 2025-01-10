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


#region TEMPORARY FIX FOR MISTRAL AI
# Inside the @retry decorator, the wrong type is caught.
# This is a temporary fix to ensure that the MistralAIEmbeddings class works as expected.
import httpx
from typing import List
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
class MistralAIEmbeddings(MistralAIEmbeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document texts.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        try:
            batch_responses = []

            @retry(
                retry=retry_if_exception_type(httpx.HTTPStatusError),
                wait=wait_fixed(self.wait_time),
                stop=stop_after_attempt(self.max_retries),
            )
            def _embed_batch(batch: List[str]):
                response = self.client.post(
                    url="/embeddings",
                    json=dict(
                        model=self.model,
                        input=batch,
                    ),
                )
                response.raise_for_status()
                return response

            for batch in self._get_batches(texts):
                batch_responses.append(_embed_batch(batch))
            return [
                list(map(float, embedding_obj["embedding"]))
                for response in batch_responses
                for embedding_obj in response.json()["data"]
            ]
        except Exception as e:
            raise
#endregion
# mapping between the types and the corresponding LangChain EmbeddingModel class
EMBEDDING_MODEL_TYPE_TO_EMBEDDING_MODEL = {
    # EmbeddingModelTypes.OPENAI: OpenAIEmbeddings,
    EmbeddingModelTypes.OLLAMA: OllamaEmbeddings,
    EmbeddingModelTypes.MISTRAL: MistralAIEmbeddings,
}