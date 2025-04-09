import os
import requests
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_45")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME_45")
api_version = os.getenv("AZURE_API_VERSION_45")
api_key = os.getenv("AZURE_OPENAI_API_KEY_45")

url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about GPT-4.5."}
    ]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Response:", response.json()["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)
