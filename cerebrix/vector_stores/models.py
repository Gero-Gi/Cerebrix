from django.db import models
from common.models.mixins import TimestampUserModel, TimestampModel
from encrypted_json_fields.fields import EncryptedJSONField

from vector_stores.utils.db_clients import BaseVectorDbClient
from .types import VectorStoreTypes, VectorStoreMetrics
from vector_stores.utils.db_clients import STORE_CLIENT_MAP
from aimodels.models import EmbeddingModel
from vector_stores.exceptions import VectorStoreStoreError


class VectorStoreBackend(TimestampUserModel):
    """
    This model represent a Vector Database. All the configurations to connect to a
    Vector Database are stored here.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Configuration to connect to the Vector Database
    config = EncryptedJSONField()

    type = models.IntegerField(choices=VectorStoreTypes.choices)

    embedding_model = models.ForeignKey(
        "aimodels.EmbeddingModel", on_delete=models.SET_NULL, null=True
    )

    @property
    def db_client(self) -> BaseVectorDbClient:
        return STORE_CLIENT_MAP[self.type](self)

    def __str__(self):
        return self.name


class VectorStore(TimestampUserModel):
    """
    This model represents a Vector Store.
    It is a collection of vectors that are stored in a Vector Database.
    It is the equivalent of a collection in Qdrant or an index in Pinecone.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # this will be used as collection/index name in the vector database
    code = models.CharField(max_length=255)

    backend = models.ForeignKey(
        "vector_stores.VectorStoreBackend", on_delete=models.CASCADE
    )
    # if None, the embedding model will be the one of the vector store backend
    embedding_model = models.ForeignKey(
        "aimodels.EmbeddingModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    metric = models.IntegerField(
        choices=VectorStoreMetrics.choices,
        null=True,
        blank=True,
        default=VectorStoreMetrics.COSINE,
        editable=False,
    )

    def __str__(self):
        return self.name

    def get_embedding_model(self) -> EmbeddingModel:
        return self.embedding_model or self.backend.embedding_model

    def save(self, *args, **kwargs):
        """
        Save the store both in the database and in the vector store db.
        """
        client = self.backend.db_client
        try:
            if not client.store_exists(self.code):
                client.create_store(self)
            else:
                client.update_store(self)
        except Exception as e:
            raise VectorStoreStoreError(
                message=f"Vector store {self.code} can't be saved correctly. "
                "There was an error while interacting with the vector store backend: {e}"
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete the store both in the database and in the vector store db.
        """
        client = self.backend.db_client
        if client.store_exists(self.code):
            try:
                client.delete_store(self)
            except Exception as e:
                raise VectorStoreStoreError(
                    message=f"Vector store {self.code} can't be deleted correctly. "
                    "There was an error while interacting with the vector store backend: {e}"
                )
        super().delete(*args, **kwargs)
        
        
class VectorDocument(TimestampModel):
    """
    This model represents a File that has been embedded and stored in a Vector Store.
    """
    
    store = models.ForeignKey("vector_stores.VectorStore", on_delete=models.CASCADE)

    file = models.FileField(upload_to="vector_documents/")
    
    
