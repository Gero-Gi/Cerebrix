import logging

from pydantic import BaseModel, Field, field_validator, ValidationError
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance

from vector_stores.exceptions import VectorStoreValidationError
from vector_stores.types import VectorStoreMetrics
from .base import BaseVectorDbClient

logger = logging.getLogger(__name__)


class QdrantConfig(BaseModel):
    host: str = Field(..., min_length=1)
    port: int = Field(..., gt=0, lt=65536)    
    
    @field_validator('host')
    def validate_host(cls, v):
        import re
        # Hostname/IP regex pattern that includes localhost, IPv4, and domain names
        pattern = r'^(localhost|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$'
        
        if not re.match(pattern, v):
            raise ValidationError('Invalid hostname format')
        return v

class CerebrixQdrantClient(BaseVectorDbClient):
    """
    Qdrant client for Cerebrix.
    
    In Qdrant, the store is called a collection.
    """
    config_schema = QdrantConfig
    def __init__(self, backend: "VectorStoreBackend"):
        super().__init__(backend)
        self.client = QdrantClient(host=self.config["host"], port=self.config["port"])
    
    def store_exists(self, store_name: str):
        return self.client.collection_exists(store_name)
    
    def get_distance(self, metric: VectorStoreMetrics):
        mapping = {
            VectorStoreMetrics.COSINE: Distance.COSINE,
            VectorStoreMetrics.EUCLIDEAN: Distance.EUCLID,
            VectorStoreMetrics.DOT_PRODUCT: Distance.DOT,
            VectorStoreMetrics.MANHATTAN: Distance.MANHATTAN,
        }
        return mapping[metric]
    
    def create_store(self, store: "VectorStore"):
        self.client.create_collection(
            collection_name=store.code,
            vectors_config={
                "size": store.get_embedding_model().size,
                "distance": self.get_distance(store.metric)
            }
        )
    
    def delete_store(self, store: "VectorStore"):
        self.client.delete_collection(store.code)
