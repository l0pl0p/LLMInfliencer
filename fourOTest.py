from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY_4o"),
    api_version=os.getenv("AZURE_API_VERSION_4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_4o")
    
    )


deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME_4o") # explicitly from your Azure portal

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about GPT-4.5."}
    ]
)

print("Response:", response.choices[0].message.content)

