# MedRouter

MedRouter is a Python library designed to facilitate the interaction with various APIs for medical AI applications. Currently, it supports segmentation models, with plans to expand into other domains soon. This project is powered by PYCAD.

## Features

- **Easy API Integration**: Simplifies the process of calling different APIs hosted on external servers.
- **Segmentation Models**: Supports segmentation models with more models and domains to be added in the future.
- **Error Handling**: Provides robust error handling to ensure smooth operation.

## Installation

You can install MedRouter using pip:
```bash
pip install medrouter
```

## Usage

Here's a quick example of how to use the MedRouter library:
```python
from medrouter import MedRouter

# Initialize the client with your API key
client = MedRouter(api_key="your_api_key")

# Run a segmentation model
predictions = client.segmentation.create(
    source="path_to_file",
    model="total-segmentator"
)

print(predictions)
```

## Available Models

- **total-segmentator**: A model for comprehensive segmentation tasks.

## Error Handling

MedRouter provides specific exceptions to handle common errors:

- `ModelNotFoundError`: Raised when the specified model is not found.
- `InferenceError`: Raised when there is an error during the inference process.
- `APIKeyError`: Raised when there is an issue with the API key, such as it being missing or incorrect.

## Contributing

We welcome contributions to expand the capabilities of MedRouter. Please feel free to submit issues or pull requests.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more details.

## Contact

For more information, please contact us at [contact@pycad.co](mailto:contact@pycad.co).

---

MedRouter is a project by PYCAD, dedicated to advancing medical AI technologies.