from medrouter.client import MedRouter
import time

client = MedRouter(api_key="your API key")

while True:
    response = client.segmentation.get("request_id")
    print("Current response:", response)

    if response.get("status") == "processed" or response.get("status") == "failed":
        break

    print("Checking again in 10 seconds...")
    time.sleep(10)