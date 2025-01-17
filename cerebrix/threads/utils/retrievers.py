from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.documents import Document

from cerebrix.threads.models import Thread


class BaseThreadRetriever(Runnable):
    def __init__(self, thread: Thread):
        self.thread = thread

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list[Document]:
        raise NotImplementedError()


class VectorStoreThreadRetriever(BaseThreadRetriever): 

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list[Document]:
        pass
        rag = self.thread.backend.vector_store.rag_backend
        vector_store = rag.vector_store
        
        db_client = vector_store.get_db_client()
        retriever = db_client.get_retriever(vector_store)
        return retriever.invoke(input)
