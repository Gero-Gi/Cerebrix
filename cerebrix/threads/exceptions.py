from common.exceptions import CerebrixError

class TokenLimitExceededError(CerebrixError):
    """
    Raised when the token limit is exceeded
    """
    code = "token_limit_exceeded"
    message = "The token limit is exceeded"
    status_code = 400
