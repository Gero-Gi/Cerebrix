from django.test import TestCase


from vector_stores.models import VectorStoreBackend, VectorStore
from vector_stores.types import VectorStoreTypes, VectorStoreMetrics
from vector_stores.utils.db_clients import CerebrixQdrantClient
from aimodels.models import EmbeddingModel
from aimodels.types import EmbeddingModelTypes


class QdrantVectorStoreTests(TestCase):
    def setUp(self):
        self.backend = VectorStoreBackend.objects.create(
            name="Test Qdrant Backend",
            type=VectorStoreTypes.QDRANT,
            config={"host": "localhost", "port": 6333},
            embedding_model=EmbeddingModel.objects.create(
                name="Test Embedding Model",
                code="test_embedding_model",
                type=EmbeddingModelTypes.OLLAMA,
                size=1024,
            ),
        )
        
        self.client = self.backend.db_client
        

    def test_store_lifecycle(self):
        """Test creating and deleting a store in Qdrant"""

        store = VectorStore.objects.create(
            name="Test Store",
            code="test_store",
            backend=self.backend,
            metric=VectorStoreMetrics.COSINE,
        )

        # Verify store exists in Qdrant
        self.assertTrue(
            self.client.store_exists(store.code),
            "Store should exist in Qdrant after creation",
        )

        # Delete store
        store.delete()

        # Verify store was deleted from Qdrant
        self.assertFalse(
            self.client.store_exists(store.code),
            "Store should not exist in Qdrant after deletion",
        )
