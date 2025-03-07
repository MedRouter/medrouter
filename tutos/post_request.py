from medrouter.client import MedRouter

client = MedRouter(api_key="your API key")

post_message = client.segmentation.post(
    source="path to nifti or zip (dicoms) file",
    model="total-segmentator",
    model_id=570,
    prechecks=False
)

print("Post message:", post_message)