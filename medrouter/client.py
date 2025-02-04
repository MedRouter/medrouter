import requests
from .config import AVAILABLE_MODELS
from .exceptions import ModelNotFoundError, InferenceError, APIKeyError

class MedRouter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.segmentation = Segmentation(api_key)

class Segmentation:
    def __init__(self, api_key):
        self.api_key = api_key

    def create(self, source, model, prechecks=False):
        if model not in AVAILABLE_MODELS:
            raise ModelNotFoundError(f"Model '{model}' not found. Available models: {', '.join(AVAILABLE_MODELS)}")

        url = "https://api.medrouter.co/api/inference/use/"
        headers = {"Authorization": self.api_key}
        data = {"model": model}

        try:
            with open(source, "rb") as file:
                files = {"file": file}
                response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 500:
                raise APIKeyError("Error running inference: 500 Server Error. This may indicate that the API key is missing or incorrect.")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Error running inference: {e}")

    def info(self):
        return "This class handles segmentation API calls. Use the 'create' method to run inference." 