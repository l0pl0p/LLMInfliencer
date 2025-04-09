from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_4o"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_4o"),
    api_version=os.getenv("AZURE_API_VERSION_4o"),
)

BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
AI_PRODUCT_NAME = os.getenv("AI_PRODUCT_NAME")

class QueryRequest(BaseModel):
    product_name: str = AI_PRODUCT_NAME
    model: str = os.getenv("AZURE_DEPLOYMENT_NAME_4o")

class QueryResponse(BaseModel):
    response_text: str

class JudgeRequest(BaseModel):
    product_name: str
    response_text: str
    judge_model: str = os.getenv("AZURE_DEPLOYMENT_NAME_4o")

class JudgeDecision(BaseModel):
    knows_product: bool
    explanation: str

def search_bing(query: str, count: int = 3):
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_API_KEY}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML", "count": count}
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()
    results = response.json()
    snippets = [item["snippet"] for item in results.get("webPages", {}).get("value", [])]
    return "\n\n".join(snippets)

def query_llm(request: QueryRequest) -> QueryResponse:
    web_context = search_bing(request.product_name)
    prompt = f"""
    Using the latest available web information below, answer the question:

    Web Information:
    {web_context}

    Question: What do you know about the AI product '{request.product_name}'?
    """
    completion = client.chat.completions.create(
        model=request.model,
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = completion.choices[0].message.content.strip()
    return QueryResponse(response_text=response_text)

def judge_llm(request: JudgeRequest) -> JudgeDecision:
    judge_prompt = f"""
    You are an expert judge AI. Determine if the following LLM response demonstrates genuine knowledge of the specified AI product.

    Product Name: {request.product_name}

    LLM Response:
    {request.response_text}

    Clearly state your decision starting with \"Decision: YES\" or \"Decision: NO\", and briefly explain your reasoning.
    """
    completion = client.chat.completions.create(
        model=request.judge_model,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    explanation = completion.choices[0].message.content.strip()
    knows_product = explanation.startswith("Decision: YES")
    return JudgeDecision(knows_product=knows_product, explanation=explanation)

# Example usage
if __name__ == "__main__":
    product_query = QueryRequest()
    query_result = query_llm(product_query)

    print("LLM Query Response with Web Grounding:")
    print(query_result.response_text)
    print("\n---\n")

    judge_request = JudgeRequest(
        product_name=product_query.product_name,
        response_text=query_result.response_text
    )
    judge_result = judge_llm(judge_request)

    print("Judge Evaluation:")
    print(judge_result.explanation)

    query_found_product = "not found" not in query_result.response_text.lower()

    if query_found_product:
        print("Feedback: 👍 (Query found product)")
        if judge_result.knows_product:
            print("Feedback: 👍 (Judge correctly assessed YES)")
        else:
            print("Feedback: 👎 (Judge incorrectly assessed NO)")
    else:
        print("Feedback: 👎 (Query did NOT find product)")
