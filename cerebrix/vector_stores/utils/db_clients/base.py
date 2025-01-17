import logging

from langchain_core.documents import Document as LangchainDocument

from vector_stores.exceptions import VectorStoreValidationError
from vector_stores.models import VectorStore

from pydantic import ValidationError

logger = logging.getLogger(__name__)

class BaseVectorDbClient:
    """
    Base class for all vector database clients.
    This class is used to abstract the main logics needed by Cerebrix to interact with a vector database.
    """
    config_schema = None
    
    def __init__(self, backend):
        self.backend = backend
        self.config = backend.config
        self.validate_config(self.config)

    def create_store(self, store: "VectorStore"):
        pass
 
    def update_store(self, store: "VectorStore"):
        pass
    
    def delete_store(self, store: "VectorStore"):
        pass
    
    def store_exists(self, store: "VectorStore"):
        pass
    
    def store_documents(self, store: "VectorStore", documents: list[LangchainDocument], payloads: list[str] = None) -> list[str]:
        """
        Store a list of documents in the vector database and return the ids of the created vectors.

        Args:
            store: The vector store to store the documents in
            documents: A list of LangchainDocument objects to store in the vector database
            payloads: A list of strings to associate with the embeddings instead of the document page_content.
        """
        pass
    
    def delete_documents(self, store: "VectorStore", ids: list[str]):
        pass
    
    @classmethod
    def validate_config(cls, config: dict):
        if not cls.config_schema:
            logger.warning(f"No config schema for {cls.__name__}")
            return True
        try:
            validated = cls.config_schema.model_validate(config)
            return validated
        except ValidationError as e:
            raise VectorStoreValidationError(message=str(e))
        
    def get_retriever(self, store: VectorStore, **kwargs):
        """ This method should return a retriever for the vector store """
        pass

