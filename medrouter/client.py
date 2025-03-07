import os
import tempfile
import zipfile
import requests
import SimpleITK as sitk
from .config import AVAILABLE_MODELS, ACCEPTED_FILE_TYPES, TASKS, ACCEPTED_EXTRA_OUTPUTS_TYPES
from .exceptions import ModelNotFoundError, InferenceError, APIKeyError, UnsupportedFileTypeError, PrecheckError, InvalidModelIDError, InvalidExtraOutputTypeError, MissingRequestIDError

class MedRouter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.segmentation = Segmentation(api_key)

class Segmentation:
    def __init__(self, api_key):
        self.api_key = api_key

    def create(self, source, model: str, model_id: int, extra_output_type: str = None, notes: str = "", prechecks=False):
        if model not in AVAILABLE_MODELS:
            raise ModelNotFoundError(f"Model '{model}' not found. Available models: {', '.join(AVAILABLE_MODELS)}")
            
        # Verify model_id exists in TASKS
        if model_id not in TASKS:
            raise InvalidModelIDError(f"Model ID '{model_id}' not found. Available model IDs: {', '.join(map(str, TASKS.keys()))}")

        # Verify extra_output_type if provided
        if extra_output_type is not None and extra_output_type not in ACCEPTED_EXTRA_OUTPUTS_TYPES:
            raise InvalidExtraOutputTypeError(f"Invalid extra output type: '{extra_output_type}'. Accepted types: {', '.join(ACCEPTED_EXTRA_OUTPUTS_TYPES)}")

        # Verify file type
        if not any(source.endswith(ext) for ext in ACCEPTED_FILE_TYPES):
            raise UnsupportedFileTypeError(f"Unsupported file type. Accepted types: {', '.join(ACCEPTED_FILE_TYPES)}")

        # Perform prechecks if requested
        if prechecks:
            self._perform_prechecks(source)

        # Proceed with API call
        url = "https://api.medrouter.co/api/inference/use/"
        headers = {"Authorization": self.api_key}
        data = {
                    "model": model,
                    "model_id": model_id,
                    "extra_output_type": extra_output_type,
                    "notes": notes,
        }

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
    
    def get_response(self, request_id):
        """
        Get the response for a specific request using its ID.
        
        Args:
            request_id: The ID of the request to retrieve.
            
        Returns:
            The response data as a JSON object.
            
        Raises:
            MissingRequestIDError: If the request_id is None.
            InferenceError: If there is an error retrieving the response.
        """
        if request_id is None:
            raise MissingRequestIDError("Request ID cannot be None. Please provide a valid request ID.")
            
        url = f"https://api.medrouter.co/api/requests/{request_id}"
        headers = {
            "Authorization": self.api_key,
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 500:
                raise APIKeyError("Error getting response: 500 Server Error. This may indicate that the API key is missing or incorrect.")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Error getting response: {e}")

    def _perform_prechecks(self, source):
        try:
            import SimpleITK as sitk
        except ImportError:
            print("SimpleITK is required for prechecks. Install it using 'pip install SimpleITK'.")
            return

        if source.endswith(('.nii', '.nii.gz')):
            self._check_nifti_file(source)
        elif source.endswith('.zip'):
            self._check_zip_file(source)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file type for precheck. Accepted types: {', '.join(ACCEPTED_FILE_TYPES)}")

    def _check_nifti_file(self, source):
        try:
            image = sitk.ReadImage(source)
            print("NIFTI file is valid and can be opened.")
        except Exception as e:
            raise PrecheckError(f"Failed to open NIFTI file: {e}")

    def _check_zip_file(self, source):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(source, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                dicom_files = [f for f in os.listdir(temp_dir) if self._is_dicom(os.path.join(temp_dir, f))]
                if len(dicom_files) >= 50:
                    print("ZIP file contains sufficient valid DICOM files.")
                else:
                    raise PrecheckError("Insufficient valid DICOM files found in ZIP.")
            except Exception as e:
                raise PrecheckError(f"Failed to process ZIP file: {e}")

    def _is_dicom(self, file_path):
        try:
            image = sitk.ReadImage(file_path)
            return True
        except Exception:
            return False

    def info(self):
        return "This class handles segmentation API calls. Use the 'create' method to run inference." 