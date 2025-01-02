from .base import BaseVectorDbClient
from .qdrant import CerebrixQdrantClient


from vector_stores.types import VectorStoreTypes

STORE_CLIENT_MAP = {
    VectorStoreTypes.QDRANT: CerebrixQdrantClient,
}
