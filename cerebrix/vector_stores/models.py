from django.db import models
from common.models.mixins import TimestampUserModel, TimestampModel
from encrypted_json_fields.fields import EncryptedJSONField
from django.contrib.postgres.fields import ArrayField


from .types import VectorStoreTypes, VectorStoreMetrics
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
    def db_client(self):
        from vector_stores.utils.db_clients import STORE_CLIENT_MAP
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
            raise VectorStoreStoreError(f"Vector store {self.code} can't be saved correctly. "
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
                raise VectorStoreStoreError(f"Vector store {self.code} can't be deleted correctly. "
                    "There was an error while interacting with the vector store backend: {e}"
                )
        super().delete(*args, **kwargs)


class Document(TimestampModel):
    """
    This model represents a File uploaded by the user.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="documents/")

    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    
    public = models.BooleanField(default=False)
    
    # hash of the preprocessed file content (XXH64)
    hash = models.CharField(max_length=16, null=True, blank=True, default=None)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        super().save(*args, **kwargs)
  


class VectorDocument(TimestampModel):
    """
    This model represents a File that has been embedded and stored in a Vector Store.
    """

    store = models.ForeignKey("vector_stores.VectorStore", on_delete=models.CASCADE)

    # documents loaded from different users but with the same hash
    documents = models.ManyToManyField("vector_stores.Document", related_name="vector_documents")
    
    hash = models.CharField(max_length=16, null=True, blank=True, default=None)
    
    embedding_ids = ArrayField(models.CharField(max_length=32), null=True, blank=True, default=None)
    
    def __str__(self):
        return f"{self.store.name} - {self.hash}"
    
    def delete(self, *args, **kwargs):
        try:
            if self.embedding_ids:
                self.store.backend.db_client.delete_documents(self.store, self.embedding_ids)
        except Exception as e:
            message = f"Vector store {self.store.code} can't be deleted correctly. "
            
            raise VectorStoreStoreError( f"VectorDocument with hash {self.hash} in vector store {self.store.code} can't be deleted correctly. "
                f"There was an error while interacting with the vector store backend: {str(e)}"
            )
        super().delete(*args, **kwargs)
        
    