import logging

from vector_stores.exceptions import VectorStoreValidationError

from pydantic import ValidationError

logger = logging.getLogger(__name__)

class BaseVectorDbClient:
    """
    Base class for all vector database clients.
    This class is used to abstract the main logics needed by Cerebrix to interact with a vector database.
    """
    config_schema = None
    
    def __init__(self, backend: "VectorStoreBackend"):
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

