from medrouter.client import MedRouter

client = MedRouter(api_key="your API key")

response = client.segmentation.process(
    source="your input files path (local)",
    model="total-segmentator",
    model_id=258,
    prechecks=False,
    extra_output_type="ply",
    notes="The patient has issue in the liver",
    check_interval=15, # how many seconds we wait before running a new request to get the response
    max_retries=2, # how many times we retry while the status is still not processed
    verbose=True
)

print("Final response:", response)