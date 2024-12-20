from django.db import models

class VectorStoreTypes(models.IntegerChoices):
    """
    The types of vector stores that are supported by the system.
    """

    QDRANT = 1, "Qdrant"
    

class VectorStoreMetrics(models.IntegerChoices):
    """
    The metrics that are supported by the vector stores.
    """

    COSINE = 1, "Cosine"
    EUCLIDEAN = 2, "Euclidean"
    DOT_PRODUCT = 3, "Dot Product"
    MANHATTAN = 4, "Manhattan"
