class ModelNotFoundError(Exception):
    """Raised when the specified model is not found in the available models list."""
    pass

class InferenceError(Exception):
    """Raised when there is an error during the inference process."""
    pass

class APIKeyError(Exception):
    """Raised when there is an issue with the API key, such as it being missing or incorrect."""
    pass

class UnsupportedFileTypeError(Exception):
    """Raised when the input file type is not supported."""
    pass

class PrecheckError(Exception):
    """Raised when there is an error during the precheck process."""
    pass

class InvalidModelIDError(Exception):
    """Raised when the provided model_id is not found in the available tasks."""
    pass

class InvalidExtraOutputTypeError(Exception):
    """Raised when the provided extra_output_type is not in the list of accepted types."""
    pass

class MissingRequestIDError(Exception):
    """Raised when the request_id is missing or None."""
    pass 