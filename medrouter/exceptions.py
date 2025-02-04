class ModelNotFoundError(Exception):
    """Raised when the specified model is not found in the available models list."""
    pass

class InferenceError(Exception):
    """Raised when there is an error during the inference process."""
    pass

class APIKeyError(Exception):
    """Raised when there is an issue with the API key, such as it being missing or incorrect."""
    pass 