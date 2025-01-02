from common.exceptions import CerebrixError


class VectorStoreBackendError(CerebrixError):
    code = "vector_store_backend_error"
    message = "An error occurred while interacting with the vector store backend."
    http_status = 500


class VectorStoreValidationError(CerebrixError):
    code = "vector_store_validation_error"
    message = "An error occurred while validating the vector store configuration."
    http_status = 400


class VectorStoreStoreError(CerebrixError):
    code = "vector_store_store_error"
    message = "An error occurred while interacting with the vector store."
    http_status = 500
