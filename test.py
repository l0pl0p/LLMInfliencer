from dotenv import load_dotenv
import os

# Force loading the .env file explicitly
load_dotenv(dotenv_path=".env", verbose=True)

# Print variables for debugging
print("Loaded endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT_4o"))
print("Loaded API version:", os.getenv("AZURE_API_VERSION_4o"))
print("Loaded deployment name:", os.getenv("AZURE_DEPLOYMENT_NAME_4o"))
